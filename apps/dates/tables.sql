BEGIN;
CREATE TABLE "dates_date" (
    "id" integer NOT NULL PRIMARY KEY,
    "slug" varchar(50) NOT NULL,
    "startdate" date NOT NULL,
    "starttime" time NULL,
    "enddate" datetime NOT NULL,
    "summary" varchar(250) NOT NULL,
    "description" text NOT NULL,
    "organizer_id" integer NULL,
    "location_id" integer NULL,
    "adress_id" integer NULL,
    "owner_id" integer NULL REFERENCES "auth_user" ("id"),
    "created" datetime NOT NULL,
    "modified" datetime NOT NULL,
    "publish" bool NOT NULL,
    "allowcomments" bool NOT NULL
)
;
CREATE TABLE "dates_organizer" (
    "id" integer NOT NULL PRIMARY KEY,
    "name" varchar(100) NOT NULL,
    "slug" varchar(50) NOT NULL
)
;
CREATE TABLE "dates_adress" (
    "id" integer NOT NULL PRIMARY KEY,
    "street" varchar(100) NOT NULL,
    "city" varchar(100) NOT NULL,
    "country" varchar(100) NOT NULL,
    "zipcode" varchar(20) NOT NULL,
    "lat" real NULL,
    "long" real NULL
)
;
CREATE TABLE "dates_location" (
    "id" integer NOT NULL PRIMARY KEY,
    "name" varchar(100) NOT NULL,
    "slug" varchar(50) NOT NULL,
    "contactmail" varchar(75) NOT NULL,
    "adress_id" integer NULL UNIQUE REFERENCES "dates_adress" ("id"),
    "icon" varchar(100) NULL
)
;
CREATE INDEX "dates_date_slug" ON "dates_date" ("slug");
CREATE INDEX "dates_date_organizer_id" ON "dates_date" ("organizer_id");
CREATE INDEX "dates_date_location_id" ON "dates_date" ("location_id");
CREATE INDEX "dates_date_adress_id" ON "dates_date" ("adress_id");
CREATE INDEX "dates_date_owner_id" ON "dates_date" ("owner_id");
CREATE INDEX "dates_organizer_slug" ON "dates_organizer" ("slug");
CREATE INDEX "dates_location_slug" ON "dates_location" ("slug");
COMMIT;
