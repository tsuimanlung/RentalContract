import os
import uuid
from datetime import datetime

from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, send_from_directory, abort
)
from flask_login import (
    LoginManager, login_user, logout_user, login_required, current_user
)

from config import Config
from models import db, User, Property, Contract, Photo, RentalHistory, schema_repair
from forms import LoginForm, PropertyForm, ContractForm, PhotoForm


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Ensure instance folder exists
    os.makedirs(os.path.join(app.root_path, 'instance'), exist_ok=True)

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = '请先登录以访问此页面。'
    login_manager.login_message_category = 'warning'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # ---- Chinese labels for templates ----
    @app.context_processor
    def inject_zh_labels():
        return dict(
            status_labels={'vacant': '空置', 'rented': '已租', 'maintenance': '维修中'},
            type_labels={'apartment': '公寓', 'house': '房屋', 'condo': '公寓',
                         'studio': '单间', 'commercial': '商铺', 'land': '地块', 'other': '其他'},
            photo_type_labels={'indoor': '室内', 'outdoor': '室外', 'facade': '外观', 'other': '其他'},
        )

    # ---- helpers ----

    def save_upload(file_obj, subdir):
        """Save an uploaded file with a unique name and return the filename."""
        ext = file_obj.filename.rsplit('.', 1)[1].lower() if '.' in file_obj.filename else 'bin'
        unique = f'{uuid.uuid4().hex}.{ext}'
        dest = os.path.join(app.config['UPLOAD_FOLDER'], subdir, unique)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        file_obj.save(dest)
        return unique

    # ---- init db & default user ----

    with app.app_context():
        db.create_all()
        schema_repair(db)  # add missing columns to existing DBs
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print('默认用户已创建: admin / admin123')

    # ========================  AUTH  ========================

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user and user.check_password(form.password.data):
                login_user(user)
                next_page = request.args.get('next')
                flash(f'欢迎回来, {user.username}!', 'success')
                return redirect(next_page or url_for('dashboard'))
            flash('用户名或密码错误。', 'danger')
        return render_template('login.html', form=form)

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('您已退出登录。', 'info')
        return redirect(url_for('login'))

    # ====================  DASHBOARD  =======================

    @app.route('/')
    @login_required
    def dashboard():
        properties = Property.query.order_by(Property.updated_at.desc()).all()
        total = len(properties)
        rented = sum(1 for p in properties if p.status == 'rented')
        vacant = sum(1 for p in properties if p.status == 'vacant')
        maint = sum(1 for p in properties if p.status == 'maintenance')
        return render_template(
            'dashboard.html',
            properties=properties,
            total=total, rented=rented, vacant=vacant, maintenance=maint
        )

    # ==================  PROPERTY CRUD  ====================

    @app.route('/property/new', methods=['GET', 'POST'])
    @login_required
    def add_property():
        form = PropertyForm()
        if form.validate_on_submit():
            prop = Property(
                name=form.name.data,
                address=form.address.data,
                property_type=form.property_type.data,
                status=form.status.data,
                description=form.description.data,
            )
            db.session.add(prop)
            db.session.flush()  # get prop.id before commit

            # 如果添加房源时同时录入租客信息，自动创建合同
            if form.tenant_name.data and form.lease_start.data and form.lease_end.data:
                contract = Contract(
                    property_id=prop.id,
                    tenant_name=form.tenant_name.data,
                    tenant_id_card=form.tenant_id_card.data,
                    tenant_phone=form.tenant_phone.data,
                    start_date=form.lease_start.data,
                    end_date=form.lease_end.data,
                    rent_amount=0,
                )
                db.session.add(contract)
                if prop.status == 'vacant':
                    prop.status = 'rented'

            db.session.commit()
            flash(f'房源 "{prop.name}" 添加成功！', 'success')
            return redirect(url_for('property_detail', pid=prop.id))
        return render_template('property_form.html', form=form, title='添加房源')

    @app.route('/property/<int:pid>')
    @login_required
    def property_detail(pid):
        prop = Property.query.get_or_404(pid)
        contracts = prop.contracts.all()
        photos = prop.photos.all()
        histories = prop.rental_histories.all()
        return render_template(
            'property_detail.html',
            property=prop,
            contracts=contracts,
            photos=photos,
            histories=histories,
            contract_form=ContractForm(),
            photo_form=PhotoForm(),
        )

    @app.route('/property/<int:pid>/edit', methods=['GET', 'POST'])
    @login_required
    def edit_property(pid):
        prop = Property.query.get_or_404(pid)
        form = PropertyForm(obj=prop)
        if form.validate_on_submit():
            form.populate_obj(prop)
            db.session.commit()
            flash('房源信息已更新！', 'success')
            return redirect(url_for('property_detail', pid=prop.id))
        return render_template(
            'property_form.html', form=form, title='编辑房源', property=prop
        )

    @app.route('/property/<int:pid>/delete', methods=['POST'])
    @login_required
    def delete_property(pid):
        prop = Property.query.get_or_404(pid)
        name = prop.name

        # Remove associated files from disk
        for c in prop.contracts:
            if c.file_path:
                _rm(os.path.join(app.config['UPLOAD_FOLDER'], 'contracts', c.file_path))
        for p in prop.photos:
            if p.file_path:
                _rm(os.path.join(app.config['UPLOAD_FOLDER'], 'photos', p.file_path))

        db.session.delete(prop)
        db.session.commit()
        flash(f'房源 "{name}" 已删除。', 'success')
        return redirect(url_for('dashboard'))

    # ======================  CONTRACTS  =====================

    @app.route('/property/<int:pid>/contract', methods=['POST'])
    @login_required
    def add_contract(pid):
        prop = Property.query.get_or_404(pid)
        form = ContractForm()
        if form.validate_on_submit():
            contract = Contract(
                property_id=pid,
                tenant_name=form.tenant_name.data,
                tenant_id_card=form.tenant_id_card.data,
                tenant_phone=form.tenant_phone.data,
                start_date=form.start_date.data,
                end_date=form.end_date.data,
                rent_amount=form.rent_amount.data,
                deposit=form.deposit.data,
                notes=form.notes.data,
            )
            if form.contract_file.data:
                contract.file_path = save_upload(form.contract_file.data, 'contracts')

            db.session.add(contract)
            if prop.status == 'vacant':
                prop.status = 'rented'
            db.session.commit()
            flash('合同已添加！', 'success')
        else:
            for field, errs in form.errors.items():
                for e in errs:
                    flash(f'{field}: {e}', 'danger')
        return redirect(url_for('property_detail', pid=pid))

    @app.route('/contract/<int:cid>/delete', methods=['POST'])
    @login_required
    def delete_contract(cid):
        contract = Contract.query.get_or_404(cid)
        pid = contract.property_id
        if contract.file_path:
            _rm(os.path.join(app.config['UPLOAD_FOLDER'], 'contracts', contract.file_path))
        db.session.delete(contract)
        db.session.commit()
        flash('合同已删除。', 'success')
        return redirect(url_for('property_detail', pid=pid))

    @app.route('/uploads/contracts/<filename>')
    @login_required
    def download_contract(filename):
        return send_from_directory(
            os.path.join(app.config['UPLOAD_FOLDER'], 'contracts'), filename
        )

    # =======================  PHOTOS  =======================

    @app.route('/property/<int:pid>/photo', methods=['POST'])
    @login_required
    def add_photo(pid):
        Property.query.get_or_404(pid)
        form = PhotoForm()
        if form.validate_on_submit():
            photo = Photo(
                property_id=pid,
                photo_type=form.photo_type.data,
                description=form.description.data,
                file_path=save_upload(form.photo_file.data, 'photos'),
            )
            db.session.add(photo)
            db.session.commit()
            flash('照片已上传！', 'success')
        else:
            for field, errs in form.errors.items():
                for e in errs:
                    flash(f'{field}: {e}', 'danger')
        return redirect(url_for('property_detail', pid=pid))

    @app.route('/photo/<int:phid>/delete', methods=['POST'])
    @login_required
    def delete_photo(phid):
        photo = Photo.query.get_or_404(phid)
        pid = photo.property_id
        _rm(os.path.join(app.config['UPLOAD_FOLDER'], 'photos', photo.file_path))
        db.session.delete(photo)
        db.session.commit()
        flash('照片已删除。', 'success')
        return redirect(url_for('property_detail', pid=pid))

    @app.route('/uploads/photos/<filename>')
    @login_required
    def serve_photo(filename):
        return send_from_directory(
            os.path.join(app.config['UPLOAD_FOLDER'], 'photos'), filename
        )

    # ====================  RENTAL HISTORY  ==================

    @app.route('/property/<int:pid>/end-tenancy', methods=['POST'])
    @login_required
    def end_tenancy(pid):
        """End the current active contract and move it to rental history."""
        prop = Property.query.get_or_404(pid)
        active = prop.contracts.first()
        if active:
            history = RentalHistory(
                property_id=pid,
                tenant_name=active.tenant_name,
                tenant_id_card=active.tenant_id_card,
                tenant_phone=active.tenant_phone,
                start_date=active.start_date,
                end_date=datetime.utcnow().date() if hasattr(datetime, 'utcnow') else datetime.now().date(),
                rent_amount=active.rent_amount,
                deposit=active.deposit,
                notes=f'从当前合同 #{active.id} 转入历史',
            )
            db.session.add(history)
            db.session.delete(active)

        prop.status = 'vacant'
        db.session.commit()
        flash('租约已结束，已归档至历史记录。', 'success')
        return redirect(url_for('property_detail', pid=pid))

    # =======================  UTILS  ========================

    def _rm(path):
        try:
            if os.path.exists(path):
                os.remove(path)
        except OSError:
            pass

    return app


# ---- entrypoint ----
if __name__ == '__main__':
    application = create_app()
    application.run(debug=True, host='0.0.0.0', port=5000)
