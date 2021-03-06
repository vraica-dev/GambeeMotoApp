from flask import render_template, redirect, request, url_for, session, flash
from werkzeug.urls import url_parse
from flask import current_app as app
from flask_login import LoginManager, current_user, login_user, login_manager, login_required, logout_user
from application import db
from application.models import TripRecords, Riders, MechanicalEvent
from datetime import datetime
from components.riderProfile import RiderProfile

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
            session['logged_user'] = valid_rider.email
            login_user(valid_rider)
            return redirect(url_for('home'))
        else:
            flash('Wrong Email or Password. Try Again!')
            session.clear()
            return redirect(url_for('login_page'))
    else:
        session.clear()
        return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup_page():
    session.clear()

    if request.method == 'POST':
        new_email = request.form['new_email']
        new_passw = request.form['new_passw']
        new_passw_second = request.form['new_passw']

        new_rider = Riders.query.filter_by(email=new_email).first()
        new_rider_add = Riders(new_email, new_passw)
        new_rider_add.set_passw(new_passw)
        if new_rider is None and new_passw == new_passw_second:
            db.session.add(new_rider_add)
            db.session.commit()
            return redirect(url_for('login_page'))
        else:
            return render_template('signup.html')
            session.clear()
    else:
        session.clear()
        return render_template('signup.html')


@app.route('/home')
@login_required
def home():
    if session.get('logged_user', None) is not None:
        return render_template('home.html', crr_user=session['logged_user'].split('@')[0])
    else:
        return redirect(url_for('login_page'))


@app.route('/trips', methods=['GET', 'POST'])
@login_required
def trips():
    if session.get('logged_user', None) is not None:

        if request.method == 'GET':
            return render_template('trips.html', crr_user=session['logged_user'].split('@')[0])

        if request.method == 'POST':
            temp_trip_name = request.form['trip_name']
            temp_trip_date = datetime.fromisoformat(request.form['trip_date'])
            temp_area_name = request.form['area_name']
            temp_km_travelled = int(request.form['km_travelled'])
            temp_hours_riding = int(request.form['hours_riding'])
            temp_km_initial = int(request.form['km_initial'])
            temp_km_final = int(request.form['km_final'])
            temp_added_by = session['logged_user']

            if session.get('logged_user', None) == 'guest@guest.com':
                flash("Sorry. You can't save data as Guest.")
            else:

                new_trip = TripRecords(trip_name=temp_trip_name, trip_date=temp_trip_date, area_name=temp_area_name,
                                       km_travelled=temp_km_travelled,
                                       h_travelled=temp_hours_riding, km_initial=temp_km_initial,
                                       km_final=temp_km_final, added_by=temp_added_by)
                db.session.add(new_trip)
                db.session.commit()

            return redirect(url_for('trips'))

    else:
        return redirect(url_for('login_page'))


@app.route('/view_trips', methods=['GET'])
@login_required
def view_trips():
    if session['logged_user'] != app.config['ADMIN_USER']:
        trips = TripRecords.query.filter_by(added_by=session['logged_user']).all()
    else:
        trips = TripRecords.query.all()

    return render_template('view_trips.html', list_trips=trips, crr_user=session['logged_user'].split('@')[0])


@app.route('/<trip_name>')
@login_required
def detailed_trip(trip_name):
    if session['logged_user'] != app.config['ADMIN_USER']:
        found_trip = TripRecords.query.filter_by(trip_name=trip_name, added_by=session['logged_user']).first()
    else:
        found_trip = TripRecords.query.filter_by(trip_name=trip_name).first()

    return render_template('detailed_trip.html', detailed_trip=found_trip,
                           crr_user=session['logged_user'].split('@')[0])


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/ap')
@login_required
def admin_pannel():
    if session['logged_user'] != app.config['ADMIN_USER']:
        return redirect(url_for('login_page'))
    else:

        all_users = Riders.query.all()
        all_posts = TripRecords.query.all()
        return render_template('admin_pannel.html', users=all_users, trip_posts=all_posts)


@app.route('/logout')
def log_out():
    logout_user()
    session.clear()
    return redirect(url_for('login_page'))


@app.route('/delete/<rider_email>')
def delete_user(rider_email):
    if session['logged_user'] == app.config['ADMIN_USER']:
        found_user = Riders.query.filter_by(email=rider_email).first()
        db.session.delete(found_user)
        db.session.commit()
        return redirect(url_for('admin_pannel'))
    else:
        return redirect(url_for('login_page'))


@app.route('/delete_trip/<rider_email>/<trip_name>')
def delete_trip(rider_email, trip_name):
    if session['logged_user'] != 'guest@guest.com':
        found_trip = TripRecords.query.filter_by(added_by=rider_email, trip_name=trip_name).first()
        db.session.delete(found_trip)
        db.session.commit()

        if session['logged_user'] == app.config['ADMIN_USER']:
            return redirect(url_for('admin_pannel'))
        else:
            return redirect(url_for('view_trips'))

    else:
        flash("Guest user cannot delete posts.")
        return redirect(url_for('view_trips'))


@app.route('/update_trip/<rider_email>/<trip_name>', methods=['POST'])
def update_existing_trip(rider_email, trip_name):
    temp_trip_name = request.form['new_trip_name']
    temp_trip_date = datetime.fromisoformat(request.form['new_trip_date'])
    temp_area_name = request.form['new_area_name']
    temp_km_travelled = int(request.form['new_km_travelled'])
    temp_hours_riding = int(request.form['new_hours_riding'])
    temp_km_initial = int(request.form['new_km_initial'])
    temp_km_final = int(request.form['new_km_final'])
    temp_added_by = rider_email

    trip_existing = TripRecords.query.filter_by(added_by=rider_email, trip_name=trip_name).first()
    updated_trip = TripRecords(trip_name=temp_trip_name, trip_date=temp_trip_date, area_name=temp_area_name,
                               km_travelled=temp_km_travelled,
                               h_travelled=temp_hours_riding, km_initial=temp_km_initial,
                               km_final=temp_km_final, added_by=temp_added_by)

    db.session.delete(trip_existing)
    db.session.commit()

    db.session.add(updated_trip)
    db.session.commit()

    return redirect(url_for('view_trips'))


@app.route('/user/<rider_email>')
def user_panel(rider_email):
    active_user = Riders.query.filter(Riders.email.startswith(rider_email)).first()

    fulL_user = RiderProfile(active_user.email, active_user.joined_on)
    fulL_user.set_tripDB(TripRecords)
    fulL_user.set_meventsDB(MechanicalEvent)
    fulL_user.get_user_recordset()
    fulL_user.get_mechanical_recordset()

    return render_template('user_panel.html', rider_email=fulL_user)


@app.route('/mechanical_event', methods=['GET', 'POST'])
@login_required
def mechanical_event():
    if session.get('logged_user', None) is not None:

        if request.method == 'GET':
            return render_template('mechanical_event.html', crr_user=session['logged_user'].split('@')[0])

        if request.method == 'POST':
            temp_event_name = request.form['mevent_name']
            temp_event_date = datetime.fromisoformat(request.form['mevent_date'])
            temp_event_details = request.form['mevent_details']
            temp_event_km = request.form['mevent_km']
            temp_event_cost = request.form['mevent_cost']
            temp_event_owner = session['logged_user']

            if session.get('logged_user', None) == 'XXguest@guest.com':
                flash("Sorry. You can't save data as Guest.")
            else:

                new_event = MechanicalEvent(event_name=temp_event_name, event_date=temp_event_date,
                                            event_details=temp_event_details, event_km=temp_event_km,
                                            event_cost=temp_event_cost, event_owner=temp_event_owner)
                db.session.add(new_event)
                db.session.commit()

            return redirect(url_for('mechanical_event'))

    else:
        return redirect(url_for('login_page'))


@app.route('/view_mechanical_ev', methods=['GET'])
@login_required
def view_mechanical_ev():
    if session['logged_user'] != app.config['ADMIN_USER']:
        mevents = MechanicalEvent.query.filter_by(event_owner=session['logged_user']).all()
    else:
        mevents = MechanicalEvent.query.all()

    return render_template('view_mechanical_ev.html', mevents=mevents, crr_user=session['logged_user'].split('@')[0])


@loginMan.user_loader
def load_user(email):
    return Riders.query.filter_by(email=email).first()
