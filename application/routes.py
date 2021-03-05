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
            session['logged_user'] =  valid_rider.email
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
        return render_template('home.html', crr_user=session['logged_user'].split('@')[0] )
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
            temp_area_name = request.form['area_name']
            temp_km_travelled = int(request.form['km_travelled'])
            temp_hours_riding = int(request.form['hours_riding'])
            temp_km_initial = int(request.form['km_initial'])
            temp_km_final = int(request.form['km_final'])
            temp_added_by = session['logged_user']

            if session.get('logged_user', None) == 'guest@guest.com':
                flash("Sorry. You can't save data as Guest.")
            else:

                new_trip = TripRecords(trip_name=temp_trip_name, area_name=temp_area_name, km_travelled=temp_km_travelled,
                                       h_travelled=temp_hours_riding, km_initial=temp_km_initial, km_final=temp_km_final, added_by=temp_added_by)
                db.session.add(new_trip)
                db.session.commit()

            return redirect(url_for('trips'))

    else:
        return redirect(url_for('login_page'))


@app.route('/view_trips', methods=['GET'])
@login_required
def view_trips():
    if session['logged_user'] != 'admin@gmail.com':
        trips = TripRecords.query.filter_by(added_by=session['logged_user'] ).all()
    else:
        trips = TripRecords.query.all()

    return render_template('view_trips.html', list_trips=trips, crr_user=session['logged_user'].split('@')[0])


@app.route('/<trip_name>')
@login_required
def detailed_trip(trip_name):
    if session['logged_user'] != 'admin@gmail.com':
        found_trip = TripRecords.query.filter_by(trip_name=trip_name, added_by=session['logged_user'] ).all()
    else:
        found_trip = TripRecords.query.filter_by(trip_name=trip_name).all()

    return render_template('detailed_trip.html', detailed_trip=found_trip)


@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/ap')
@login_required
def admin_pannel():
    if session['logged_user'] != 'admin@gmail.com':
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
    if session['logged_user'] == 'admin@gmail.com':
        found_user = Riders.query.filter_by(email=rider_email).first()
        db.session.delete(found_user)
        db.session.commit()
        return redirect(url_for('admin_pannel'))
    else:
        return redirect(url_for('login_page'))


@app.route('/delete_trip/<rider_email>/<trip_name>')
def delete_trip(rider_email, trip_name):
    if session['logged_user'] == 'admin@gmail.com':
        found_trip = TripRecords.query.filter_by(added_by=rider_email, trip_name=trip_name).first()
        db.session.delete(found_trip)
        db.session.commit()
        return redirect(url_for('admin_pannel'))
    else:
        return redirect(url_for('login_page'))






@loginMan.user_loader
def load_user(email):
    return Riders.query.filter_by(email=email).first()



