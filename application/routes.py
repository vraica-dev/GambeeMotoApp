from flask import render_template, redirect, request, url_for
from flask import current_app as app
from application import db
from application.model import TripRecords


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
