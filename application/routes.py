from flask import render_template, redirect, request, url_for, session, flash
from werkzeug.urls import url_parse
from flask import current_app as app
from flask_login import LoginManager, current_user, login_user, login_manager, login_required, logout_user
from application import db
from application.models import TripRecords, Riders

loginMan = LoginManager(app)
login_manager.session_protection = "strong"


@app.route('/', methods=['GET', 'POST'])
def login_page():
    session.clear()

    if request.method == 'POST':
        rider_email = request.form['rider_email']
        rider_passw = request.form['rider_passw']

        valid_rider = Riders.query.filter_by(email=rider_email).first()

        if valid_rider is not None and valid_rider.check_password(rider_passw):
            login_user(valid_rider)
            return redirect(url_for('home'))
        else:
            flash('Wrong Email or Password. Try Again!')
            session.clear()
            return redirect(url_for('login_page'))
    else:
        session.clear()
        return render_template('login.html')


@app.route('/home')
@login_required
def home():
    return render_template('home.html')


@app.route('/trips', methods=['GET', 'POST'])
@login_required
def trips():
    if request.method == 'GET':
        return render_template('trips.html')

    if request.method == 'POST':
        temp_trip_name = request.form['trip_name']
        temp_area_name = request.form['area_name']
        temp_km_travelled = int(request.form['km_travelled'])
        temp_hours_riding = int(request.form['hours_riding'])
        temp_km_initial = int(request.form['km_initial'])
        temp_km_final = int(request.form['km_final'])

        new_trip = TripRecords(trip_name=temp_trip_name, area_name=temp_area_name, km_travelled=temp_km_travelled,
                               h_travelled=temp_hours_riding, km_initial=temp_km_initial, km_final=temp_km_final)
        db.session.add(new_trip)
        db.session.commit()

        return redirect(url_for('trips'))


@app.route('/view_trips', methods=['GET'])
def view_trips():
    trips = TripRecords.query.all()
    return render_template('view_trips.html', list_trips=trips)


@app.route('/<trip_name>')
def detailed_trip(trip_name):
    found_trip = TripRecords.query.filter_by(trip_name=trip_name).all()
    return render_template('detailed_trip.html', detailed_trip=found_trip)


@app.route('/logout')
def log_out():
    logout_user()
    session.clear()
    return redirect(url_for('login_page'))


@loginMan.user_loader
def load_user(email):
    print(email)
    return Riders.query.filter_by(email=email).first()



