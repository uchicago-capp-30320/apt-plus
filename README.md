# Apartments Plus
Tenants struggle to navigate scattered information when searching for a new apartment. Without a centralized solution to aggregate key information, renters must take significant time to research or risk unforeseen downsides. This is exacerbated by popular commercial platforms' incentive to hide negative aspects of their listings. As generalist platforms, they also lack granularity in neighborhood details, for example, a distance to grocery stores known to local residents.

Apartments Plus aggregates broad data with a focus on those that mainstream rental sites do not display, such as building defects and landlord reputations. Apartments Plus is currently focused on tenants in a university neighborhood like Hyde Park which welcomes a steady influx of new tenants every year but neighborhood-specific information such as university transportation routes that are not available on major rental sites.

## Installation
As of May 6, 2025, Apartments Plus is currently in an early development stage. To contribute:

- Clone the repo
- Run `uv install` to set up the relevant Python environment
- Install [GDAL](https://gdal.org/en/stable/index.html), an open source geodata library, to run the server locally.

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

## Folder structure

Our current folder structure uses the basic geoDjango template. Backend features will be in the `/app_app` and `/app_proj` directories, where frontend views will be in the `/apt_app/templates/` directory.

As we develop the product more, we will add more guidance on code location and specific features.

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
