1. Get started wit heroku account
2. Install the client
 - heroku help
3. Create and upload the website
    - heroku create djangodeploylibrary
4.  We can then push our app to the Heroku repository as shown below.  This will upload the app, package it in a dyno, run collectstatic, and start the site. 
       - git push heroku main


5. If we're lucky, the app is now "running" on the site, but it won't be working properly because we haven't set up the database tables for use by our application. To do this we need to use the heroku run command and start a "one off dyno" to perform a migrate operation. Enter the following command in your terminal:

    - heroku run python manage.py migrate

6.  We're also going to need to be able to add books and authors, so lets also create our administration superuser, again using a one-off dyno:
   -  heroku run python manage.py createsuperuser

 Once this is complete, we can look at the site. It should work, although it won't have any books in it yet. To open your browser to the new website, use the command

 7.  - heroku open
   Create some books in the admin site, and check out whether the site is behaving as you expect

 8. Manage addons
     > heroku addons

Add-on                                     Plan       Price  State
─────────────────────────────────────────  ─────────  ─────  ───────
heroku-postgresql (postgresql-flat-26536)  hobby-dev  free   created
 └─ as DATABASE  
 more details using the below commands
 heroku addons:open heroku-postgresql
  
9. Setting configuration variables
If you recall from the section on getting the website ready to publish, we have to set environment variables for DJANGO_SECRET_KEY and DJANGO_DEBUG. Let's do this now.
> heroku config:set DJANGO_SECRET_KEY="
uxrcp7&h+czhm$$f0j@%4z^&d(yg7pfzf+ifuz%=0(r8-j4xhn"

We similarly set DJANGO_DEBUG:
> heroku config:set DJANGO_DEBUG='False'

if you visit the site now you'll get a "Bad request" error, because the ALLOWED_HOSTS setting is required if you have DEBUG=False (as a security measure). Open /locallibrary/settings.py and change the ALLOWED_HOSTS setting to include your base app url (e.g. 'locallibrary1234.herokuapp.com') and the URL you normally use on your local development server.

ALLOWED_HOSTS = ['<your app URL without the https:// prefix>.herokuapp.com','127.0.0.1']
# For example:
# ALLOWED_HOSTS = ['fathomless-scrubland-30645.herokuapp.com', '127.0.0.1']

Then save your settings and commit them to your Github repo and to Heroku:
git add -A
git commit -m 'Update ALLOWED_HOSTS with site and development server URL'
git push origin main
git push heroku main

 Note

After the site update to Heroku completes, enter a URL that does not exist (e.g. /catalog/doesnotexist/). Previously this would have displayed a detailed debug page, but now you should just see a simple "Not Found" page.

Debugging
# Show current logs
heroku logs

# Show current logs and keep updating with any new results
heroku logs --tail

# Add additional logging for collectstatic (this tool is run automatically during a build)
heroku config:set DEBUG_COLLECTSTATIC=1

# Display dyno status
heroku ps





