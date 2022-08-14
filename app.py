#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import logging
from logging import Formatter, FileHandler
from typing import List

import babel
import dateutil.parser
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy

from forms import *

#----------------------------------------------------------------------------#
# App Config
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website_link = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String)
    show_id = db.Column(db.Integer, db.ForeignKey('Show.id'))
    shows = db.relationship("Show", foreign_keys=[show_id], backref='Venue')

    def to_json(self):
      return {
        "id": self.id,
        "name": self.name,
        "city": self.city,
        "state": self.state,
        "address": self.address,
        "phone": self.phone,
        "genres": self.genres.split(","),
        "image_link": self.image_link,
        "website_link": self.website_link,
        "facebook_link": self.facebook_link,
        "seeking_talent": self.seeking_talent,
        "seeking_description": self.seeking_description,
        "show_id": self.show_id
      }

    def past_shows(self):
      today = datetime.now()
      return Show.query.filter(Show.id == self.show_id, Show.start_time < today).all()

    def upcoming_shows(self):
      today = datetime.now()
      return Show.query.filter(Show.id == self.show_id, Show.start_time > today).all()


    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website_link = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_venue  = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String)
    show = db.relationship('Show', backref='Artist', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
  __tablename__ = 'Show'

  id = db.Column(db.Integer, primary_key=True)
  start_time = db.Column(db.DateTime)
  venue_id = db.Column(db.Integer, db.ForeignKey("Venue.id"))
  artist_id = db.Column(db.Integer, db.ForeignKey("Artist.id"))
  artist = db.relationship("Artist")

  def to_json(self):
    return {
      "artist_id": self.artist.id,
      "artist_name": self.artist.name,
      "artist_image_link": self.artist.image_link,
      "start_time": self.start_time
    }



#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.\

  # query db for all venu objects
  all_venues = Venue.query.all()
  # define data list to pass to front end for rendering
  data = []
  # define a list of json representations of all venue objects
  json_rep_all_venues = []

  # convert all venue objects from db into their correspondent json representations
  for each_venue in all_venues:
    # convert single venue object from db into it's json representation
    json_rep_one_venue = each_venue.to_json()
    # update the json representation above with number of upcoming shows
    json_rep_one_venue['num_upcoming_shows'] = len(each_venue.upcoming_shows())
    # store json representation of one object into a list
    json_rep_all_venues.append(json_rep_one_venue)
  # create json object for displaying data in frontend
  for json_rep_one_venue in json_rep_all_venues:
    render_venue = {}
    render_venue['city'] = json_rep_one_venue['city']
    render_venue['state'] = json_rep_one_venue['state']
    render_venue['venues'] = [{
      "id": json_rep_one_venue['id'],
      "name": json_rep_one_venue['name'],
      "num_upcoming_shows": json_rep_one_venue['num_upcoming_shows']
    }]
    data.append(render_venue)

  # data=[{
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "venues": [{
  #     "id": 1,
  #     "name": "The Musical Hop",
  #     "num_upcoming_shows": 0,
  #   }, {
  #     "id": 3,
  #     "name": "Park Square Live Music & Coffee",
  #     "num_upcoming_shows": 1,
  #   }]
  # }, {
  #   "city": "New York",
  #   "state": "NY",
  #   "venues": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }]
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  # get search term
  search_term = request.form['search_term']

  # retrive venues matching search term
  venues = Venue.query.filter(Venue.name.ilike(f"%{search_term}%")).all()
  results = {}
  results['count'] = len(venues)
  results['data'] = []

  for venue in venues:
    results['data'].append({'id': venue.id, 'name': venue.name})
  print(f'Results are: {results}')
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  return render_template('pages/search_venues.html', results=results, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  # retrieve venue
  venue = Venue.query.get(venue_id)

  if venue:
    # retrieve show data
    upcoming_shows = venue.upcoming_shows()
    past_shows = venue.past_shows()

    data = {
      'id': venue.id,
      'name': venue.name,
      'genres': venue.genres,
      'address': venue.address,
      'city': venue.city,
      'state': venue.state,
      'phone': venue.phone,
      'website_link': venue.website_link,
      'facebook_link': venue.facebook_link,
      'seeking_talent': venue.seeking_talent,
      'seeking_description': venue.seeking_description,
      'image_link': venue.image_link,
      'past_shows': [show.to_json() for show in past_shows],
      'upcoming_shows': [show.to_json() for show in upcoming_shows],
      'past_shows_count': len(past_shows),
      'upcoming_shows_count': len(upcoming_shows)
    }
  else:
    flash("Error occured: Invalid ID reference.")
    print("Throw error")
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  error = False
  try:
    name = request.form['name']
    genres = request.form['genres']
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']
    phone = request.form['phone']
    website_link = request.form['website_link']
    image_link = request.form['image_link']
    facebook_link = request.form['facebook_link']
    seeking_talent = request.form['seeking_talent']
    seeking_description = request.form['seeking_description']

    venue = Venue(name=name, genres=genres, city=city, state=state, address=address, phone=phone,
                  website_link=website_link, image_link=image_link, facebook_link=facebook_link,
                  seeking_talent=seeking_talent, seeking_description=seeking_description)
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    error = True
    flash('An error occured.' + request.form['name'] + 'could not be listed.')
    db.session.rollback()
  finally:
    db.session.close()

  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    flash('Venue' + venue.name + 'was successfully deleted!')
  except:
    db.session.rollback()
    flash('An error has occurred,' + venue.name + 'could not be deleted.')
  finally:
    db.session.close()

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None
#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = []
  artists = Artist.query.all()
  for artist in artists:
    artists_information = {
      'id': artist.id,
      'name': artist.name,
    }
    data.append(artists_information)
  # data=[{
  #   "id": 4,
  #   "name": "Guns N Petals",
  # }, {
  #   "id": 5,
  #   "name": "Matt Quevedo",
  # }, {
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  # }]
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form['search_term']
  artists = Artist.query.filter(Artist.name.ilike(f"%{search_term}%")).all()

  results = {}
  results['count'] = len(artists)
  results['data'] = []

  for artist in artists:
    results['data'].append({'id': artist.id, 'name': artist.name})

  print(f'Results are: {results}')
  return render_template('pages/search_artists.html', results=results, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  data = []
  artists = Artist.query.get(artist_id)
  if artists:
    number_of_shows = Show.query.filter_by(artist_id = artists.id ).all()
    past_shows = []
    upcoming_shows = []

    print(f"Number of shows: {number_of_shows}")

    for show in number_of_shows:
      print(f"Investigating show: {show}")
      venue = Venue.query.get(show.venue_id)
      print(f"Retreived venue: {venue}")
      if venue:
        shows = {
          'venue_id': show.venue_id,
          'venue_name': venue.name,
          'venue_image_link': venue.image_link,
          'start_time': show.start_time
        }
      print(f"Show start time: {show.start_time}")

    data = {
      "id": artists.id,
      "name": artists.name,
      "genres": artists.genres,
      "city": artists.city,
      "state": artists.state,
      "phone": artists.phone,
      "website_link": artists.website_link,
      "facebook_link": artists.facebook_link,
      "seeking_description": artists.seeking_description,
      "image_link": artists.image_link,
    }
  else:
    flash("Artist does not exist.")
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artists = {}
  # artist={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  # }
  # TODO: populate form with fields from artist with ID <artist_id>
  artists = Artist.query.get(artist_id)
  artist = {
    'id': artists.id,
    'name': artists.name
  }
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form_submited = ArtistForm(request.form)
  if not form_submited.validate():
    flash('An error occured in your input !')
    return render_template('forms/edit_artist.html', form=form_submited)

  artists = Artist.query.get(artist_id)

  artists.name = request.form['name']
  artists.city = request.form['city']
  artists.state = request.form['state']
  artists.phone = request.form['phone']
  artists.facebook_link = request.form['facebook_link']
  artists.image_link = request.form['image_link']
  artists.website_link = request.form['website_link']

  db.session.add(artists)
  db.session.commit()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  # TODO: populate form with values from venue with ID <venue

  form = VenueForm()
  venues = {}
  venues = Venue.query.get(venue_id)
  venue = {
    'id': venues.id,
    'name': venues.name
  }
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form_submited = VenueForm(request.form)
  if not form_submited.validate():
    flash('An error occured in your input !')
    return render_template('forms/edit_venue.html', form=form_submited)

  venues = Venue.query.get(venue_id)

  venues.name = request.form['name']
  venues.genres = request.form['genres']
  venues.city = request.form['city']
  venues.state = request.form['state']
  venues.address = request.form['address']
  venues.phone = request.form['phone']
  venues.website_link = request.form['website_link']
  venues.image_link = request.form['image_link']
  venues.facebook_link = request.form['facebook_link']

  db.session.add(venues)
  db.session.commit()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  error = False
  try:
    name = request.form['name']
    genres = request.form['genres']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    image_link = request.form['image_link']
    website_link = request.form['website_link']
    facebook_link = request.form['facebook_link']
    seeking_venue = request.form.get('seeking_venue')
    seeking_venue = True if seeking_venue else False

    artists = Artist(name=name, genres=genres, city=city, state=state, phone=phone, image_link=image_link,
                     website_link=website_link, facebook_link=facebook_link, seeking_venue=seeking_venue)
    db.session.add(artists)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    error = True
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    flash('Artist' + request.form['name'] + 'could not be listed.')
    db.session.rollback()
  finally:
    db.session.close()
  # TODO: modify data to be the data object returned from db insertion
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data = []
  shows = Show.query.all()
  for show in shows:
    venue = Venue.query.filter_by(id=show.venue_id).first()
    print(venue.name)
    artist = Artist.query.filter_by(id=show.artist_id).first()
    print(artist.name, artist.image_link)
    show_data = {
      'venue_id': show.venue_id,
      'venue_name': venue.name,
      'artist_id': show.artist_id,
      'artist_name': artist.name,
      'artist_image_link': artist.image_link,
      'start_time': str(show.start_time)
    }
    data.append(show_data)
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  error = False
  try:
    artist_id = request.form['artist_id']
    venue_id = request.form['venue_id']
    start_time = request.form['start_time']
    shows = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
    db.session.add(shows)
    db.session.commit()
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
    error= True
    flash('An error occured. Show could not be listed.')
    db.session.rollback()
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
