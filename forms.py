from flask_wtf import FlaskForm
from wtforms import SubmitField, IntegerField, FloatField, SelectField
from wtforms.validators import DataRequired, NumberRange

from core.object import Role


class GeneratePlayerPoolForm(FlaskForm):
    total_player = IntegerField('Total Player', 
                                validators=[DataRequired(), NumberRange(min=100)])
    pct_player_join_team = FloatField('Percentage of Player Join Team',
                                  validators=[NumberRange(min=0, max=1)])
    mutation_rate = FloatField('Mutation Rate',
                               validators=[NumberRange(min=0, max=1)])
    submit = SubmitField('Submit')
    
class InputtedPlayerForm(FlaskForm):
    mmr = IntegerField('MMR', validators=[DataRequired()])
    role = SelectField('Role', 
                       choices=[(role.value, role.name.capitalize()) for role in Role], 
                       validators=[DataRequired()])
    submit = SubmitField('Submit')
