from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField, TextAreaField, FloatField, DateField,
    SelectField, PasswordField, SubmitField
)
from wtforms.validators import DataRequired, Optional, Length, NumberRange, EqualTo


class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(max=80)])
    password = PasswordField('密码', validators=[DataRequired()])
    submit = SubmitField('登录')


class PropertyForm(FlaskForm):
    name = StringField('房源名称', validators=[DataRequired(), Length(max=200)])
    address = TextAreaField('地址', validators=[DataRequired()])
    property_type = SelectField('房源类型', choices=[
        ('apartment', '公寓'),
        ('house', '房屋'),
        ('condo', '高层公寓'),
        ('studio', '单间'),
        ('commercial', '商铺'),
        ('land', '地块'),
        ('other', '其他')
    ])
    status = SelectField('状态', choices=[
        ('vacant', '空置'),
        ('rented', '已租'),
        ('maintenance', '维修中')
    ])
    description = TextAreaField('描述', validators=[Optional()])

    # 租客信息（添加房源时可同时录入）
    tenant_name = StringField('租客姓名', validators=[Optional(), Length(max=200)])
    tenant_id_card = StringField('身份证号码', validators=[Optional(), Length(max=50)])
    tenant_phone = StringField('联系电话', validators=[Optional(), Length(max=50)])
    lease_start = DateField('租期开始', validators=[Optional()])
    lease_end = DateField('租期结束', validators=[Optional()])

    submit = SubmitField('保存')


class ContractForm(FlaskForm):
    tenant_name = StringField('租客姓名', validators=[DataRequired(), Length(max=200)])
    tenant_id_card = StringField('身份证号码', validators=[Optional(), Length(max=50)])
    tenant_phone = StringField('联系电话', validators=[Optional(), Length(max=50)])
    start_date = DateField('开始日期', validators=[DataRequired()])
    end_date = DateField('结束日期', validators=[DataRequired()])
    rent_amount = FloatField('月租金（¥）', validators=[DataRequired(), NumberRange(min=0)])
    deposit = FloatField('押金（¥）', validators=[Optional(), NumberRange(min=0)])
    contract_file = FileField('合同文件（PDF或图片）', validators=[
        Optional(),
        FileAllowed(['pdf', 'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'], '仅支持PDF或图片格式')
    ])
    notes = TextAreaField('备注', validators=[Optional()])
    submit = SubmitField('添加合同')


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('当前密码', validators=[DataRequired()])
    new_password = PasswordField('新密码', validators=[DataRequired(), Length(min=6, max=80)])
    confirm_password = PasswordField('确认新密码', validators=[
        DataRequired(), EqualTo('new_password', message='两次密码输入不一致')
    ])
    submit = SubmitField('修改密码')


class PhotoForm(FlaskForm):
    photo_type = SelectField('照片类型', choices=[
        ('indoor', '室内'),
        ('outdoor', '室外'),
        ('facade', '外观'),
        ('other', '其他')
    ])
    photo_file = FileField('照片', validators=[
        DataRequired(),
        FileAllowed(['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'], '仅支持图片格式')
    ])
    description = StringField('描述', validators=[Optional(), Length(max=200)])
    submit = SubmitField('上传')
