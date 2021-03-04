from flask import render_template, redirect, request, url_for
from flask import current_app as app
from . import db
from .model import TripRecords


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/trips', methods=['GET', 'POST'])
def trips():

    if request.method == 'GET':
        return render_template('trips.html')

    if request.method == 'POST':
        temp_trip_name = request.form['trip_name']
        temp_area_name = request.form['area_name']
        temp_km_travelled = request.form['km_travelled']
        temp_hours_riding = request.form['hours_riding']
        temp_km_initial = request.form['km_initial']
        temp_km_final= request.form['km_final']

        print(temp_trip_name)

        new_trip = TripRecords(trip_name = temp_trip_name, area_name = temp_area_name, km_travelled =temp_km_travelled, h_travelled= temp_hours_riding)
        db.session.add(new_trip)
        db.session.commit()

        print('done')

        return redirect(url_for('trips'))
