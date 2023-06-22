from flask import Flask, render_template, url_for, redirect, session
from flask_paginate import Pagination
from core.algo import Generation, Individual, Team, Player, Role

from forms import GeneratePlayerPoolForm, InputtedPlayerForm


app = Flask(__name__)
app.config['SECRET_KEY'] = '8dcfd1c0328bbf2b'
app.config['WTF_CSRF_ENABLED'] = False

generation: Generation = None
player_pool_list = None
best_fitness_over_generation = []
role_img_map = {
    Role.GOLDLANE: 'goldlane.jpg',
    Role.JUNGLE: 'jungle.png',
    Role.ROAM: 'roam.jpg',
    Role.MIDLANE: 'midlane.jpg',
    Role.OFFLANE: 'offlane.jpg'
}


@app.route('/', defaults={'page': 1}, methods=['GET', 'POST'])
@app.route('/<int:page>', methods=['GET', 'POST'])    
def index(page):
    global generation, player_pool_list, role_img_map, best_fitness_over_generation
    form: GeneratePlayerPoolForm = GeneratePlayerPoolForm()
    if form.validate_on_submit():
        player_pool = Player.generate_player_pool(form.total_player.data)
        player_pool_list = list(player_pool)
        team_pool = Team.generate_team_pool(
            player_pool,
            form.pct_player_join_team.data
        )
        population = Individual.generate_population(team_pool)
        generation = Generation(population, player_pool)
        best_fitness_over_generation.append(generation.get_best_individual_fitness())
        return redirect(url_for('index'))

    limit = 12
    start = (page - 1) * limit
    end = start + limit
    if generation is not None and player_pool_list is not None:
        partial_player_pool = player_pool_list[start:end]
        pagination = Pagination(page=page, per_page=limit, total=len(player_pool_list))
        chart_data = {
            'x': [i for i in range(len(best_fitness_over_generation))],
            'y': best_fitness_over_generation
        }
        return render_template(
            'index.html', 
            form=form,
            generation_number=generation.generation_number,
            partial_player_pool=partial_player_pool,
            role_img_map=role_img_map,
            total_player=len(player_pool_list),
            total_team=len(generation.population)*2,
            total_individual=len(generation.population),
            total_player_in_population=generation.count_player_in_population(),
            pagination=pagination,
            best_fitness=f'{generation.get_best_individual_fitness():.2f}',
            best_individual_idx=generation.get_best_individual()[0],
            chart_data=chart_data
        )
    return render_template('index.html', form=form)

@app.route('/next-generation', defaults={'repeat': 1})
@app.route('/next-generation/<int:repeat>')
def next_generation(repeat):
    global generation, best_fitness_over_generation
    for _ in range(repeat):
        generation.next_generation()
        best_fitness_over_generation.append(generation.get_best_individual_fitness())

    return redirect(url_for('index'))


@app.route('/matchmaking/<int:individual_idx>')
def matchmaking(individual_idx):
    global generation, role_img_map
    return render_template(
        'Matchmaking.html',
        individual_idx=individual_idx, 
        individual=generation.population[individual_idx], 
        role_img_map=role_img_map, 
        max_idx=len(generation.population)-1
    )


@app.route('/playnowpage', methods=['GET', 'POST'])
def play_now_page():
    global generation, player_pool_list, best_fitness_over_generation
    form: InputtedPlayerForm = InputtedPlayerForm()
    if form.validate_on_submit():
        player_pool = Player.generate_player_pool(1000)
        team_pool = Team.generate_team_pool(
            player_pool,
            inputted_player=Player(form.mmr.data, Role(int(form.role.data)), is_inputted=True)
        )
        player_pool_list = list(player_pool)
        player_pool_list.sort(key=lambda x: x.is_inputted, reverse=True)
        population = Individual.generate_population(team_pool)
        generation = Generation(population, player_pool)
        best_fitness_over_generation.append(generation.get_best_individual_fitness())
        return redirect(url_for('index'))
    return render_template('PlaynowPage.html', form=form)



if __name__ == '__main__':
    app.run(debug=True)
