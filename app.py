from flask import Flask
import db
import requests

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_POOL_SIZE'] = 250
    app.config['SQLALCHEMY_POOL_RECYCLE'] = 280
    app.config['SQLALCHEMY_POOL_TIMEOUT'] = 100
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///espn_API.db?check_same_thread=False"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['MAX_THREADS'] = 50
    app.config['THREADS_PER_WORKER'] = 10
    app.config['DEBUG'] = True

    # initialize database connections
    db.db.init_app(app)
    with app.app_context():
        db.db.create_all()
        
    @app.route('/')
    def index():
        return 'Hello, World!'

    @app.route('/create_soccer_database')
    def create_soccer_database():
        try:
            with app.app_context():
                league_code = 'eng.1'
                for year in range(2001, 2024):
                    try:
                        url = f"https://site.web.api.espn.com/apis/v2/sports/soccer/{league_code}/standings?season={year}"
                        response = requests.get(url)
                        data = response.json()
                        league_name = data['name']
                        season_year = year
                        data = data['children'][0]['standings']['entries']
                        for team in data:
                            stats = team["stats"]
                            team_name = team['team']['name']
                            gp = next(s["value"] for s in stats if s["name"] == "gamesPlayed")
                            w = next(s["value"] for s in stats if s["name"] == "wins")
                            d = next(s["value"] for s in stats if s["name"] == "ties")
                            l = next(s["value"] for s in stats if s["name"] == "losses")
                            f = next(s["value"] for s in stats if s["name"] == "pointsFor")
                            a = next(s["value"] for s in stats if s["name"] == "pointsAgainst")
                            gd = next(s["value"] for s in stats if s["name"] == "pointDifferential")
                            p = next(s["value"] for s in stats if s["name"] == "points")
                            previous_entry = db.Soccer_standings.get(
                                    league_name=league_name,
                                    league_code = league_code,
                                    season_year=season_year,
                                    team_name=team_name,
                                    gp=gp,
                                    w=w,
                                    d=d,
                                    l=l,
                                    f=f,
                                    a=a,
                                    gd=gd)
                            if not previous_entry:
                                db.Soccer_standings.new(
                                        league_name=league_name,
                                        league_code = league_code,
                                        season_year=season_year,
                                        team_name=team_name,
                                        gp=gp,
                                        w=w,
                                        d=d,
                                        l=l,
                                        f=f,
                                        a=a,
                                        gd=gd,
                                        p=p)
                            else:
                                print('previously added to db')
                    except Exception as e:
                        print(e)  
        except Exception as e:
            print(e)  
            return {'code': 500, 'message': 'Internal server error.'}
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(threaded=True, host='0.0.0.0', port=8585, debug=True)
