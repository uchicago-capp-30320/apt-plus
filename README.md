# Apartments Plus
![Apartments Plus Logo](static/images/logo_color.svg)

Tenants struggle to navigate scattered information when searching for a new apartment. Without a centralized solution to aggregate key information, renters must take significant time to research or risk unforeseen downsides. This is exacerbated by popular commercial platforms' incentive to hide negative aspects of their listings. As generalist platforms, they also lack granularity in neighborhood details, for example, a distance to grocery stores known to local residents.

Apartments Plus aggregates data that mainstream rental sites often do not display, such as building defects and landlord reputations. Apartments Plus currently has data on Chicago, with a special focus fr tenants in a university neighborhood like Hyde Park which welcome a steady influx of new tenants every year.

We're online at [aptpl.us](https://www.aptpl.us).

![MIT License](https://img.shields.io/github/license/uchicago-capp-30320/apt-plus?color=133335)
![Build Status](https://github.com/uchicago-capp-30320/apt-plus/actions/workflows/ci.yml/badge.svg)

## Contributing
As of May 26, 2025, Apartments Plus is currently in development stage. We welcome contributions from anyone as long as it aligns with our contribution guidelines and is well constructed. That includes being written by humans, not AI.

To get started, find an issue on github, submit a PR, and it will be reviewed by a member of our team. If you have any questions, reach out in the issues tab, or over email.

### Installation
As of May 26, 2025, Apartments Plus is currently in development stage. To contribute:

1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/), if you haven't already.
2. Install [GDAL](https://gdal.org/en/stable/index.html), an open source geodata library, needed to run the server locally. See [our help section](#appendix-gdal-set-up) for some more specific instructions.
3. Run `uv sync` to set up the relevant Python environment
```bash
$ uv sync
```

You're good to go to start editing code! If you want to run the project locally, you'll need a bit more data:

4. Set up an .env file in `DEBUG=True` and relevant information on email and server addresses. These will be shared by current project administrators.
5. Launch the server locally.
```bash
$ uv run manage.py runserver
```

### Tech Stack
This is a [Django](https://www.djangoproject.com/) application that uses plain [JavaScript](https://developer.mozilla.org/en-US/docs/Web/JavaScript) and some [HTMX](https://htmx.org/) to handle frontend functionality. Our site is styled with [Bulma](https://bulma.io/). We use [Airflow](https://airflow.apache.org/) and [Python >3.10](https://www.python.org/downloads/) for data updates. Our data is stored on a [postgreSQL](https://www.postgresql.org/) server with [postGIS](https://postgis.net/) for geospatial support. 


### Folder Structure
We use our application folder to locate specific functionality. Please remember to follow that.
```
apt-plus/
├── .github/
│   └── workflows/  //   GitHub CI/CD files
├── apt_app/            // Django Application folder
│   ├── management/ //   Data management commands for Django
│   ├── views/      //   Each view is it's on .py file
├── config/             //   Django config files
├── docs/               //   Documentation, such as for APIs
├── notebooks/          //   Notebooks for data testing
├── scripts/            //   Data management
├── static/             // Static elements
│   ├── css/        //   All CSS styling
│   ├── js/         //   JavaScript functionality
│   └── images/     //   Static images
├──  templates/         // All HTML templates
└──  tests/             // All test files for testing
```

## Contributors

Contributors are listed, with no significance to the order of names:

| Who      | What      |
| ------------- | ------------- |
| Michael Rosenbaum | Design / Frontend & Project Management |
| Arkadeep Bandyopadhyay | Backend / Frontend engineering & Chief Architect |
| Miguel Perez | Backend / GIS specialist & Backend / Data engineer |
| Zewei (Whiskey) Liao | Lead QA Engineer & Backend Engineer |
| Rodrigo Rivarola | Front & Backend GIS Specialist |
| Magdalena Barros | Frontend Lead |
| Fuyuki Tani | Data Engineer |
| Keling Yue | Lead Backend Engineer & Data Engineer|

## Appendix: GDAL Set-up
### For Mac Users: GDAL Setup

If you're using a Mac, follow these steps:

This ensures Django can locate the required GDAL and GEOS libraries for geospatial functionality.

Reference: [Django Documentation: GeoDjango Installation](https://docs.djangoproject.com/en/5.2/ref/contrib/gis/install/)

1. **Install Homebrew** (if you don't have it yet):

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

2. **Install GDAL using Homebrew:**

```bash
brew install gdal
```

3. **Add the following to your `.env` file:**

```env
# GDAL/GEOS Settings
GDAL_LIBRARY_PATH=/opt/homebrew/lib/libgdal.dylib
GEOS_LIBRARY_PATH=/opt/homebrew/lib/libgeos_c.dylib
DYLD_LIBRARY_PATH=/opt/homebrew/lib
```

### For Windows Users: GDAL Setup

1. **Install GDAL**

[OSGeo4W](https://www.osgeo.org/projects/osgeo4w/)'s default installation for Windows will include the relevant packages. 

2. **Add GDAL to your PATH variable**

Then, your computer will need to be able to reference GDAL's functionality. To do so, you should [add the file folder](https://www.c-sharpcorner.com/article/how-to-addedit-path-environment-variable-in-windows-11/) to your PATH variable. If you let OSGeo4W install it, that will be "C:\OSGeo4W\bin" on most computers.
