from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

class webserverHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            engine = create_engine('sqlite:///restaurantmenu.db')
            Base.metadata.bind = engine
            DBSession = sessionmaker(bind = engine)
            session = DBSession()
            restaurants = session.query(Restaurant).all()

            if self.path.endswith("/restaurants"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                message = ""
                message += "<html><body>"

                # Link to craete new Restaurant
                message += "<a href='/restaurants/new'>Create a new restaurant</a>"

                # Lists the current restaurants
                for idx, restaurant in enumerate(restaurants):
                    if restaurant.id != idx:
                        restaurant.id = idx
                        session.add(restaurant)
                        session.commit()

                    message += "<p>"
                    message += restaurant.name
                    message += "<br><a href='restaurants/%s/edit'>Edit</a>" % restaurant.id
                    message += "<br><a href='restaurants/%s/delete'>Delete</a>" % restaurant.id
                    message += "</p>"
                message += "</body></html>"
                self.wfile.write(message)
                print message
                return

            if self.path.endswith("/restaurants/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                message = ""
                message += "<html><body>"
                message += "<h1>Make a new restaurant</h1>"
                message += "<form method='POST' enctype='multipart/form-data' action='/restaurants/new'>"
                message += '<input name="message" type="text" ><input type="submit" value="Submit">'
                message += "</form>"
                message += "</body></html>"
                self.wfile.write(message)
                print message
                return

            if self.path.endswith("/edit"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                restaurantId = self.path.split("/")[2]

                chosenRestaurant = session.query(Restaurant).filter_by(id = restaurantId).one()

                message = ""
                message += "<html><body>"
                message += "<h1>%s</h1>" % chosenRestaurant.name
                message += "<form method='POST' enctype='multipart/form-data' action='/restaurants/%s/edit'>" % restaurantId
                message += '<input name="message" type="text" ><input type="submit" value="Rename">'
                message += "</form>"
                message += "</body></html>"
                self.wfile.write(message)
                print message
                return

            if self.path.endswith("/delete"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                restaurantId = self.path.split("/")[2]

                chosenRestaurant = session.query(Restaurant).filter_by(id = restaurantId).one()

                message = ""
                message += "<html><body>"
                message += "<h1>Are you sure you want to delete %s?</h1>" % chosenRestaurant.name
                message += "<form method='POST' enctype='multipart/form-data' action='/restaurants/%s/delete'>" % restaurantId
                message += '<input type="submit" value="Yes">'
                message += "</form>"
                message += "</body></html>"
                self.wfile.write(message)
                print message
                return


        except IOError:
            self.send_error(404, "File not found %s" % self.path)

    def do_POST(self):
        try:
            engine = create_engine('sqlite:///restaurantmenu.db')
            Base.metadata.bind = engine
            DBSession = sessionmaker(bind = engine)
            session = DBSession()

            if self.path.endswith("/restaurants/new"):
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('message')


                newRestaurant = Restaurant(name = messagecontent[0])
                session.add(newRestaurant)
                session.commit()

                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()

            if self.path.endswith("/edit"):
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('message')

                restaurantId = self.path.split("/")[2]

                chosenRestaurant = session.query(Restaurant).filter_by(id = restaurantId).one()

                chosenRestaurant.name = messagecontent[0]
                session.add(chosenRestaurant)
                session.commit()

                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()

            if self.path.endswith("/delete"):
                restaurantId = self.path.split("/")[2]

                chosenRestaurant = session.query(Restaurant).filter_by(id = restaurantId).one()
                session.delete(chosenRestaurant)
                session.commit()

                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()

        except:
            pass


def main():
    try:
        port = 8080
        server = HTTPServer(('', port), webserverHandler)
        print "Web server runinng on port %s" % port
        server.serve_forever()


    except KeyboardInterrupt:
        print "^C entered, stopping web server..."
        server.socket.close()


if __name__ == '__main__':
    main()
