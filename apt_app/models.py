from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    UnicodeUsernameValidator,
    UserManager,
)
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.gis.db import models as gis_models
from django.contrib.postgres.indexes import GistIndex
from .mixins import LocationMixin

USERNAME_REQUIRED = settings.DJOK_USER_TYPE == "username"
EMAIL_REQUIRED = settings.DJOK_USER_TYPE.startswith("email")
if not (USERNAME_REQUIRED or EMAIL_REQUIRED):
    raise ValueError("Must set DJOK_USER_TYPE")


class OkUserManager(UserManager):
    def create_superuser(self, **kwargs):
        if "username" not in kwargs:
            kwargs["username"] = kwargs["email"]
        super().create_superuser(**kwargs)


class User(AbstractBaseUser, PermissionsMixin):
    """
    A modification of the built-in Django user that:
        - switches first_name & last_name for username & full_name
        - keeps other admin-compliant options
    """

    username_validator = UnicodeUsernameValidator()

    email = models.EmailField(_("email address"), unique=EMAIL_REQUIRED, default="")
    username = models.CharField(
        max_length=255,
        unique=True,
        validators=[username_validator] if USERNAME_REQUIRED else [],
        default="",
    )
    full_name = models.CharField(_("full name"), max_length=150, blank=True)
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    objects = OkUserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username" if USERNAME_REQUIRED else "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def save(self, *args, **kwargs):
        if EMAIL_REQUIRED and not self.username:
            self.username = self.email
        super().save(*args, **kwargs)

    def get_short_name(self):
        return self.username

    def get_full_name(self):
        return self.full_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)


# --- Custom models ---


class SavedProperty(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="saved_properties")
    property_obj = models.ForeignKey("Property", on_delete=models.CASCADE)
    address = models.CharField(max_length=512, null=False, blank=False, default="Unknown Address")
    custom_name = models.CharField(max_length=512, null=True, blank=True)
    date_saved = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(null=True, blank=True)
    rent_price = models.IntegerField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["address"]),
            models.Index(fields=["is_deleted"]),  # Add index for better query performance
        ]

    def __str__(self):
        return self.custom_name if self.custom_name else self.address

    def soft_delete(self):
        """Mark the property as deleted without removing it from the database."""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()
        return True

    def restore(self):
        """Restore a previously soft-deleted property."""
        self.is_deleted = False
        self.deleted_at = None
        self.date_saved = timezone.now()
        self.save()
        return True

    @property
    def bus_stops_by_time(self):
        """
        Return a dictionary with counts of bus stops within different walking time ranges.
        Returns:
            dict: Contains counts of stops within 5, 10, and 15 minutes, and total stops
        """
        result = {
            "within_5_min": 0,
            "within_10_min": 0,
            "within_15_min": 0,
            "total_stops": 0,
        }

        # Check if property and bus_stops exist
        if not self.property_obj or not self.property_obj.bus_stops:
            return result

        try:
            # Count stops by time buckets
            for stop in self.property_obj.bus_stops:
                # Skip invalid entries
                if not isinstance(stop, dict) or "properties" not in stop:
                    continue

                # Get distance in minutes
                minutes = stop.get("properties", {}).get("distance_min", 999)

                # Count by time buckets
                result["total_stops"] += 1

                if minutes <= 5:
                    result["within_5_min"] += 1
                if minutes <= 10:
                    result["within_10_min"] += 1
                if minutes <= 15:
                    result["within_15_min"] += 1

            return result

        except (TypeError, AttributeError) as e:
            # Log the error if needed
            print(f"Error processing bus stops time buckets: {e}")
            return result

    @property
    def unique_bus_routes(self):
        """
        Return a sorted list of unique bus routes serving this property.
        Returns:
            list: Sorted list of unique bus route numbers/names
        """
        if not self.property_obj or not self.property_obj.bus_stops:
            return []

        try:
            routes = set()
            for stop in self.property_obj.bus_stops:
                if (
                    isinstance(stop, dict)
                    and "properties" in stop
                    and "routes" in stop["properties"]
                ):
                    routes.update(stop["properties"]["routes"])
            return sorted(routes)
        except (TypeError, AttributeError) as e:
            print(f"Error extracting unique bus routes: {e}")
            return []

    @property
    def bus_routes_count(self):
        """
        Return the count of unique bus routes serving this property.
        Returns:
            int: Number of unique bus routes
        """
        return len(self.unique_bus_routes)

    @property
    def bus_routes_by_time(self):
        """
        Return a dictionary with unique bus routes within different walking time ranges.
        Returns:
            dict: Contains routes within 5, 10, and 15 minutes
        """
        result = {
            "within_5_min": [],
            "within_10_min": [],
            "within_15_min": [],
        }

        # Check if property and bus_stops exist
        if not self.property_obj or not self.property_obj.bus_stops:
            return result

        try:
            # Initialize sets to collect unique routes in each time bucket
            routes_5min = set()
            routes_10min = set()
            routes_15min = set()

            # Extract routes by time buckets
            for stop in self.property_obj.bus_stops:
                # Skip invalid entries
                if not isinstance(stop, dict) or "properties" not in stop:
                    continue

                # Get distance in minutes
                minutes = stop.get("properties", {}).get("distance_min", 999)
                stop_routes = stop.get("properties", {}).get("routes", [])

                # Add routes to appropriate time buckets
                if minutes <= 5:
                    routes_5min.update(stop_routes)
                if minutes <= 10:
                    routes_10min.update(stop_routes)
                if minutes <= 15:
                    routes_15min.update(stop_routes)

            # Convert sets to sorted lists
            result["within_5_min"] = sorted(routes_5min)
            result["within_10_min"] = sorted(routes_10min)
            result["within_15_min"] = sorted(routes_15min)

            return result

        except (TypeError, AttributeError) as e:
            # Log the error if needed
            print(f"Error processing bus routes by time: {e}")
            return result


class Property(LocationMixin, models.Model):
    id = models.AutoField(primary_key=True)
    address = models.CharField(max_length=255)
    location = gis_models.PointField()
    created_at = models.DateTimeField(auto_now_add=True)
    bus_stops = models.JSONField(null=True, blank=True)

    class Meta:
        indexes = [GistIndex(fields=["location"])]


class Violation(models.Model):
    violation_id = models.CharField(max_length=10, primary_key=True)
    violation_last_modified_date = models.DateField()
    violation_date = models.DateField()
    violation_code = models.CharField(max_length=20)
    violation_status = models.CharField(max_length=10)
    violation_status_date = models.DateField(null=True, blank=True)
    violation_description = models.TextField()
    violation_location = models.TextField()
    violation_inspector_comments = models.TextField()
    violation_ordinance = models.TextField()
    inspector_id = models.CharField(max_length=20)
    inspection_number = models.IntegerField()
    inspection_status = models.CharField(max_length=10)
    inspection_waived = models.CharField(max_length=5)
    inspection_category = models.CharField(max_length=20)  # NOTE
    department_bureau = models.CharField(max_length=50)
    address = models.CharField(max_length=100)
    street_number = models.IntegerField()
    street_direction = models.CharField(max_length=5)
    street_name = models.CharField(max_length=20)
    street_type = models.CharField(max_length=10)
    property_group = models.IntegerField()
    ssa = models.CharField(max_length=10)
    latitude = models.FloatField()
    longitude = models.FloatField()
    location = gis_models.PointField()


class Inspection(models.Model):
    inspection_id = models.AutoField(primary_key=True)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    date = models.DateField()
    result = models.CharField(max_length=50)
    notes = models.TextField()


class InspectionSummary(models.Model):
    # property = models.ForeignKey(Property, on_delete=models.CASCADE)
    address = models.CharField(max_length=255)
    summary = models.JSONField()


class CrimeType(models.TextChoices):
    OFFENSE_INVOLVING_CHILDREN = "OFFENSE INVOLVING CHILDREN", "Offense Involving Children"
    NARCOTICS = "NARCOTICS", "Narcotics"
    CRIM_SEXUAL_ASSAULT = "CRIM SEXUAL ASSAULT", "Crim Sexual Assault"
    CRIMINAL_DAMAGE = "CRIMINAL DAMAGE", "Criminal Damage"
    THEFT = "THEFT", "Theft"
    BURGLARY = "BURGLARY", "Burglary"
    SEX_OFFENSE = "SEX OFFENSE", "Sex Offense"
    ROBBERY = "ROBBERY", "Robbery"
    MOTOR_VEHICLE_THEFT = "MOTOR VEHICLE THEFT", "Motor Vehicle Theft"
    BATTERY = "BATTERY", "Battery"
    HOMICIDE = "HOMICIDE", "Homicide"
    CRIMINAL_SEXUAL_ASSAULT = "CRIMINAL SEXUAL ASSAULT", "Criminal Sexual Assault"
    OTHER_OFFENSE = "OTHER OFFENSE", "Other Offense"
    WEAPONS_VIOLATION = "WEAPONS VIOLATION", "Weapons Violation"
    DECEPTIVE_PRACTICE = "DECEPTIVE PRACTICE", "Deceptive Practice"
    STALKING = "STALKING", "Stalking"
    CRIMINAL_TRESPASS = "CRIMINAL TRESPASS", "Criminal Trespass"
    ASSAULT = "ASSAULT", "Assault"
    PROSTITUTION = "PROSTITUTION", "Prostitution"
    KIDNAPPING = "KIDNAPPING", "Kidnapping"
    ARSON = "ARSON", "Arson"
    CONCEALED_CARRY_LICENSE_VIOLATION = (
        "CONCEALED CARRY LICENSE VIOLATION",
        "Concealed Carry License Violation",
    )
    INTERFERENCE_WITH_PUBLIC_OFFICER = (
        "INTERFERENCE WITH PUBLIC OFFICER",
        "Interference with Public Officer",
    )
    PUBLIC_PEACE_VIOLATION = "PUBLIC PEACE VIOLATION", "Public Peace Violation"
    LIQUOR_LAW_VIOLATION = "LIQUOR LAW VIOLATION", "Liquor Law Violation"
    INTIMIDATION = "INTIMIDATION", "Intimidation"
    HUMAN_TRAFFICKING = "HUMAN TRAFFICKING", "Human Trafficking"
    GAMBLING = "GAMBLING", "Gambling"
    OBSCENITY = "OBSCENITY", "Obscenity"
    PUBLIC_INDECENCY = "PUBLIC INDECENCY", "Public Indecency"
    NON_CRIMINAL = "NON-CRIMINAL", "Non-Criminal"
    OTHER_NARCOTIC_VIOLATION = "OTHER NARCOTIC VIOLATION", "Other Narcotic Violation"
    RITUALISM = "RITUALISM", "Ritualism"
    DOMESTIC_VIOLENCE = "DOMESTIC VIOLENCE", "Domestic Violence"
    NON_CRIMINAL_SUBJECT_SPECIFIED = (
        "NON-CRIMINAL (SUBJECT SPECIFIED)",
        "Non-Criminal (Subject Specified)",
    )
    NON_CRIMINAL_ALT = "NON - CRIMINAL", "Non - Criminal"


class Crime(LocationMixin, models.Model):
    id = models.AutoField(primary_key=True)
    location = gis_models.PointField()
    date = models.DateTimeField()
    type = models.CharField(
        max_length=50, choices=CrimeType.choices, default=CrimeType.NON_CRIMINAL_ALT
    )
    description = models.TextField()

    class Meta:
        indexes = [GistIndex(fields=["location"])]


# --- Abstract base class ---
class LocationBasedFacilities(LocationMixin, models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    location = gis_models.PointField()

    class Meta:
        abstract = True
        indexes = [GistIndex(fields=["location"])]


class AmenityType(models.TextChoices):
    GROCERY = "grocery", "Grocery Store"
    PHARMACY = "pharmacy", "Pharmacy"
    RESTAURANT = "restaurant", "Restaurant"
    CAFE = "cafe", "Cafe"
    BAR = "bar", "Bar"
    HOSPITAL = "hospital", "Hospital"
    OTHER = "other", "Other"


class Amenity(LocationBasedFacilities):
    type = models.CharField(max_length=50, choices=AmenityType.choices, default=AmenityType.OTHER)


class TransitType(models.TextChoices):
    CTA = "cta", "CTA"
    METRA = "metra", "Metra"
    SHUTTLE = "shuttle", "UChicago Shuttle"
    DIVVY = "divvy", "Divvy Bike"
    OTHER = "other", "Other"


class TransitStop(LocationBasedFacilities):
    type = models.CharField(max_length=50, choices=TransitType.choices, default=TransitType.OTHER)


class TransitRoute(models.Model):
    route_id = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=50, choices=TransitType.choices, default=TransitType.OTHER)
    geometry = gis_models.MultiLineStringField()
    created_at = models.DateTimeField(auto_now_add=True)

    stops = models.ManyToManyField(TransitStop, related_name="routes")

    class Meta:
        indexes = [
            GistIndex(fields=["geometry"]),
        ]

    def __str__(self):
        return self.name
