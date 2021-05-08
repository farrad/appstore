"""
Queries the live API and import all releases locally for a Nextcloud version
"""
import sys

from requests import get

from . import import_app, ADMIN, BASE_URL, import_release

APPS_URL = 'https://apps.nextcloud.com/api/v1/platform/%s/apps.json'
PRIVATE_APPS_URL = BASE_URL + '/platform/%s/apps.json'

def _delitem(obj, key):
    if key in obj:
    	del obj[key]
    	return True
    if isinstance(obj,str): return False
    deleted = False
    for k, v in obj.items():
        if isinstance(v,dict):
            deleted = _delitem(v, key)
        if isinstance(v,list):
            for index in range(len(v)):
            	deleted = _delitem(v[index], key)
    return deleted

def main():
	version = sys.argv[1]
	apps = get(APPS_URL % version).json()
	private_apps = get(PRIVATE_APPS_URL % version).json()

	for app in apps:
		# Search for the App in the Private AppStore
		try:
			app_exists = next(item for item in private_apps if item['id'] == app['id'])
		except StopIteration:
			app_exists = False

		if app_exists != False:
			# Remove 'created' and 'lastModified' since they match to the date when app was first loaded to the Private AppStore rather when it was officially published
			while True:
				if _delitem(app, 'created') == False:
					break;
			while True:
				if _delitem(app_exists, 'created') == False:
					break;
			while True:
				if _delitem(app, 'lastModified') == False:
					break;
			while True:
				if _delitem(app_exists, 'lastModified') == False:
					break;
			# Ratings are apparantly not pulled. Removing...
			while True:
				if _delitem(app, 'ratingOverall') == False:
					break;
			while True:
				if _delitem(app_exists, 'ratingOverall') == False:
					break;
			while True:
				if _delitem(app, 'ratingNumOverall') == False:
					break;
			while True:
				if _delitem(app_exists, 'ratingNumOverall') == False:
					break;
			# Check for updates in the official Nextcloud AppStore
			if app == app_exists:
				continue;
		# Pulling the App...
		print("Fetching {} app...".format(app['id']))
		import_app(app['certificate'], 'signature', ADMIN)
		for release in app['releases']:
			import_release(release['download'], release['signature'],
							release['isNightly'], ADMIN)


if __name__ == '__main__':
    main()
