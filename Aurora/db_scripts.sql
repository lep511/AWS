
--
-- TOC entry 229 (class 1255 OID 16563)
-- Name: datediff(character varying, timestamp without time zone, timestamp without time zone); Type: FUNCTION; Schema: public; Owner: dbadmin
--

CREATE FUNCTION public.datediff(units character varying, start_t timestamp without time zone, end_t timestamp without time zone) RETURNS integer
    LANGUAGE plpgsql
    AS $$
   DECLARE
     diff_interval INTERVAL; 
     diff INT = 0;
     years_diff INT = 0;
   BEGIN
     IF units IN ('yy', 'yyyy', 'year', 'mm', 'm', 'month') THEN
       years_diff = DATE_PART('year', end_t) - DATE_PART('year', start_t);
 
       IF units IN ('yy', 'yyyy', 'year') THEN
         -- SQL Server does not count full years passed (only difference between year parts)
         RETURN years_diff;
       ELSE
         -- If end month is less than start month it will subtracted
         RETURN years_diff * 12 + (DATE_PART('month', end_t) - DATE_PART('month', start_t)); 
       END IF;
     END IF;
 
     -- Minus operator returns interval 'DDD days HH:MI:SS'  
     diff_interval = end_t - start_t;
 
     diff = diff + DATE_PART('day', diff_interval);
 
     IF units IN ('wk', 'ww', 'week') THEN
       diff = diff/7;
       RETURN diff;
     END IF;
 
     IF units IN ('dd', 'd', 'day') THEN
       RETURN diff;
     END IF;
 
     diff = diff * 24 + DATE_PART('hour', diff_interval); 
 
     IF units IN ('hh', 'hour') THEN
        RETURN diff;
     END IF;
 
     diff = diff * 60 + DATE_PART('minute', diff_interval);
 
     IF units IN ('mi', 'n', 'minute') THEN
        RETURN diff;
     END IF;
 
     diff = diff * 60 + DATE_PART('second', diff_interval);
 
     RETURN diff;
   END;
   $$;


ALTER FUNCTION public.datediff(units character varying, start_t timestamp without time zone, end_t timestamp without time zone) OWNER TO dbadmin;

--
-- TOC entry 208 (class 1259 OID 16486)
-- Name: customers; Type: TABLE; Schema: public; Owner: dbadmin
--

CREATE TABLE public.customers (
    customerid character varying(50) NOT NULL,
    firstname character varying(50),
    lastname character varying(50)
);


ALTER TABLE public.customers OWNER TO dbadmin;

--
-- TOC entry 207 (class 1259 OID 16483)
-- Name: customervehicles; Type: TABLE; Schema: public; Owner: dbadmin
--

CREATE TABLE public.customervehicles (
    customerid character varying(50) NOT NULL,
    vehicleid character varying(50) NOT NULL
);


ALTER TABLE public.customervehicles OWNER TO dbadmin;

--
-- TOC entry 203 (class 1259 OID 16439)
-- Name: dealergeofences; Type: TABLE; Schema: public; Owner: dbadmin
--

CREATE TABLE public.dealergeofences (
    geofenceid character varying(50),
    dealerid character varying(50),
    geometry polygon,
    polygonjson json
);


ALTER TABLE public.dealergeofences OWNER TO dbadmin;

--
-- TOC entry 202 (class 1259 OID 16436)
-- Name: dealers; Type: TABLE; Schema: public; Owner: dbadmin
--

CREATE TABLE public.dealers (
    dealerid character varying(50) NOT NULL,
    businessname character varying(100),
    address character varying(100),
    city character varying(50),
    state character varying(50),
    postalcode character varying(50),
    country character varying(100),
    "position" point,
    email character varying(100),
    phonenumber character varying(100)
);


ALTER TABLE public.dealers OWNER TO dbadmin;

--
-- TOC entry 206 (class 1259 OID 16451)
-- Name: geofenceevents; Type: TABLE; Schema: public; Owner: dbadmin
--

CREATE TABLE public.geofenceevents (
    "time" timestamp without time zone,
    geofenceid character varying(50),
    vehicleid character varying(50),
    eventtype character varying(50),
    latitude double precision,
    longitude double precision,
    "position" point,
    eventid character varying(50) NOT NULL
);


ALTER TABLE public.geofenceevents OWNER TO dbadmin;

--
-- TOC entry 212 (class 1259 OID 16544)
-- Name: dealer_gfevents; Type: VIEW; Schema: public; Owner: dbadmin
--

CREATE VIEW public.dealer_gfevents AS
 SELECT d.businessname,
    ge."time",
    ge.geofenceid,
    ge.vehicleid,
    ge.eventtype,
    ge.latitude,
    ge.longitude,
    ge."position",
    ge.eventid
   FROM public.geofenceevents ge,
    public.dealergeofences dg,
    public.dealers d
  WHERE (((ge.geofenceid)::text = (dg.geofenceid)::text) AND ((dg.dealerid)::text = (d.dealerid)::text));


ALTER TABLE public.dealer_gfevents OWNER TO dbadmin;

--
-- TOC entry 210 (class 1259 OID 16532)
-- Name: dealerexceptions; Type: TABLE; Schema: public; Owner: dbadmin
--

CREATE TABLE public.dealerexceptions (
    vehicleid character varying,
    dealerid character varying,
    "time" timestamp without time zone
);


ALTER TABLE public.dealerexceptions OWNER TO dbadmin;

--
-- TOC entry 204 (class 1259 OID 16442)
-- Name: dealervehicles; Type: TABLE; Schema: public; Owner: dbadmin
--

CREATE TABLE public.dealervehicles (
    dealerid character varying(50),
    vehicleid character varying(50) NOT NULL
);


ALTER TABLE public.dealervehicles OWNER TO dbadmin;

--
-- TOC entry 209 (class 1259 OID 16520)
-- Name: positionevents; Type: TABLE; Schema: public; Owner: dbadmin
--

CREATE TABLE public.positionevents (
    "time" timestamp with time zone,
    vehicleid character varying(50),
    latitude double precision,
    longitude double precision,
    additionaldata jsonb,
    "position" point,
    eventid character varying(50)
);


ALTER TABLE public.positionevents OWNER TO dbadmin;

--
-- TOC entry 201 (class 1259 OID 16415)
-- Name: vehicles; Type: TABLE; Schema: public; Owner: dbadmin
--

CREATE TABLE public.vehicles (
    vehicleid character varying(50) NOT NULL,
    description character varying(250),
    vin character varying(50),
    manufacturerid character varying(50),
    make character varying(50),
    model character varying(50),
    year integer,
    exteriorcolor character varying(50),
    enginetype character varying(50),
    bodytype character varying(100),
    msrp integer
);


ALTER TABLE public.vehicles OWNER TO dbadmin;

--
-- TOC entry 211 (class 1259 OID 16540)
-- Name: vehicle_dealer; Type: VIEW; Schema: public; Owner: dbadmin
--

CREATE VIEW public.vehicle_dealer AS
 SELECT d.businessname,
    v.vehicleid,
    d.dealerid,
    d.city AS dealercity,
    d.postalcode AS dealerpostalcode
   FROM public.vehicles v,
    public.dealers d,
    public.dealervehicles dv
  WHERE (((v.vehicleid)::text = (dv.vehicleid)::text) AND ((d.dealerid)::text = (dv.dealerid)::text));


ALTER TABLE public.vehicle_dealer OWNER TO dbadmin;

--
-- TOC entry 216 (class 1259 OID 16564)
-- Name: vehicle_dealer_presence; Type: VIEW; Schema: public; Owner: dbadmin
--

CREATE VIEW public.vehicle_dealer_presence AS
 SELECT DISTINCT dgf.businessname,
    dgf.vehicleid,
    s1.entertime,
    s2.exittime,
    date_part('day'::text, ((COALESCE((s2.exittime)::timestamp with time zone, now()))::timestamp without time zone - s1.entertime)) AS noofdayssincearrival
   FROM ((public.dealer_gfevents dgf
     LEFT JOIN LATERAL ( SELECT min(d1."time") AS entertime
           FROM public.dealer_gfevents d1
          WHERE (((d1.eventtype)::text = 'ENTER'::text) AND ((d1.businessname)::text = (dgf.businessname)::text) AND ((d1.vehicleid)::text = (dgf.vehicleid)::text))
          GROUP BY d1.businessname, d1.vehicleid) s1 ON (true))
     LEFT JOIN LATERAL ( SELECT max(d2."time") AS exittime
           FROM public.dealer_gfevents d2
          WHERE (((d2.eventtype)::text = 'EXIT'::text) AND ((d2.businessname)::text = (dgf.businessname)::text) AND ((d2.vehicleid)::text = (dgf.vehicleid)::text))
          GROUP BY d2.businessname, d2.vehicleid) s2 ON (true));


ALTER TABLE public.vehicle_dealer_presence OWNER TO dbadmin;

--
-- TOC entry 215 (class 1259 OID 16558)
-- Name: vehicle_details; Type: VIEW; Schema: public; Owner: dbadmin
--

CREATE VIEW public.vehicle_details AS
 SELECT v.vehicleid,
    v.description,
    v.vin,
    v.manufacturerid,
    v.make,
    v.model,
    v.year,
    v.exteriorcolor,
    v.enginetype,
    v.bodytype,
    v.msrp,
    d.dealerid,
    COALESCE(d.businessname, 'Not Assigned'::character varying(100)) AS dealername,
    d.city AS dealercity,
    d.postalcode AS dealerpostalcode
   FROM ((public.vehicles v
     LEFT JOIN public.dealervehicles dv ON (((v.vehicleid)::text = (dv.vehicleid)::text)))
     LEFT JOIN public.dealers d ON (((dv.dealerid)::text = (d.dealerid)::text)));


ALTER TABLE public.vehicle_details OWNER TO dbadmin;

--
-- TOC entry 213 (class 1259 OID 16548)
-- Name: vehicle_positionevents; Type: VIEW; Schema: public; Owner: dbadmin
--

CREATE VIEW public.vehicle_positionevents AS
 SELECT v.businessname AS alloteddealer,
    p."time",
    p.vehicleid,
    p.latitude,
    p.longitude,
    p.additionaldata,
    p."position",
    p.eventid
   FROM public.positionevents p,
    public.vehicle_dealer v
  WHERE ((p.vehicleid)::text = (v.vehicleid)::text);


ALTER TABLE public.vehicle_positionevents OWNER TO dbadmin;

--
-- TOC entry 205 (class 1259 OID 16448)
-- Name: vehiclestatus; Type: TABLE; Schema: public; Owner: dbadmin
--

CREATE TABLE public.vehiclestatus (
    vehicleid character varying(50) NOT NULL,
    intransit boolean,
    lastposition point,
    lastpositiontstamp timestamp without time zone,
    atdealer character varying,
    haveexception boolean,
    longitude double precision,
    latitude double precision
);


ALTER TABLE public.vehiclestatus OWNER TO dbadmin;

--
-- TOC entry 214 (class 1259 OID 16552)
-- Name: vehicle_status; Type: VIEW; Schema: public; Owner: dbadmin
--

CREATE VIEW public.vehicle_status AS
 SELECT vs.vehicleid,
    vs.intransit,
    vs.lastposition,
    vs.lastpositiontstamp,
    vs.atdealer,
    vs.haveexception,
    vs.longitude,
    vs.latitude,
    vd.businessname AS alloteddealer,
    vd.dealercity,
    vd.dealerpostalcode,
    vd.dealerid AS alloteddealerid,
    ( SELECT DISTINCT vd1.businessname AS atdealername
           FROM public.vehicle_dealer vd1
          WHERE ((vd1.dealerid)::text = (vs.atdealer)::text)) AS atdealername
   FROM public.vehiclestatus vs,
    public.vehicle_dealer vd
  WHERE ((vs.vehicleid)::text = (vd.vehicleid)::text);


ALTER TABLE public.vehicle_status OWNER TO dbadmin;

--
-- TOC entry 217 (class 1259 OID 16576)
-- Name: vehicles_sold; Type: VIEW; Schema: public; Owner: dbadmin
--

CREATE VIEW public.vehicles_sold AS
 SELECT v.vehicleid,
    v.description,
    v.vin,
    v.manufacturerid,
    v.make,
    v.model,
    v.year,
    v.exteriorcolor,
    v.enginetype,
    v.bodytype,
    v.msrp,
    c.firstname,
    c.lastname,
    d.businessname AS dealer
   FROM public.vehicles v,
    public.customervehicles cv,
    public.customers c,
    public.vehicle_dealer d
  WHERE (((v.vehicleid)::text = (cv.vehicleid)::text) AND ((c.customerid)::text = (cv.customerid)::text) AND ((d.vehicleid)::text = (v.vehicleid)::text));


ALTER TABLE public.vehicles_sold OWNER TO dbadmin;

--
-- TOC entry 218 (class 1259 OID 16596)
-- Name: vehicles_count_all; Type: VIEW; Schema: public; Owner: dbadmin
--

CREATE VIEW public.vehicles_count_all AS
 SELECT count(*) AS alloted,
    0 AS intransit,
    0 AS atdealer,
    0 AS sold,
    vehicle_details.dealername AS dealer
   FROM public.vehicle_details
  GROUP BY vehicle_details.dealername
UNION
 SELECT 0 AS alloted,
    0 AS intransit,
    0 AS atdealer,
    count(*) AS sold,
    vehicles_sold.dealer
   FROM public.vehicles_sold
  GROUP BY vehicles_sold.dealer
UNION
 SELECT 0 AS alloted,
    count(*) AS intransit,
    0 AS atdealer,
    0 AS sold,
    vehicle_status.alloteddealer AS dealer
   FROM public.vehicle_status
  WHERE ((vehicle_status.intransit = true) AND (vehicle_status.atdealer IS NULL))
  GROUP BY vehicle_status.alloteddealer
UNION
 SELECT 0 AS alloted,
    0 AS intransit,
    count(*) AS atdealer,
    0 AS sold,
    vehicle_status.alloteddealer AS dealer
   FROM public.vehicle_status
  WHERE ((vehicle_status.haveexception = false) AND ((vehicle_status.atdealer)::text = (vehicle_status.alloteddealerid)::text))
  GROUP BY vehicle_status.alloteddealer;


ALTER TABLE public.vehicles_count_all OWNER TO dbadmin;

--
-- TOC entry 4011 (class 0 OID 16486)
-- Dependencies: 208
-- Data for Name: customers; Type: TABLE DATA; Schema: public; Owner: dbadmin
--

INSERT INTO public.customers VALUES ('56473829', 'Jane', 'Doe');
INSERT INTO public.customers VALUES ('56437829', 'John', 'Doe');
INSERT INTO public.customers VALUES ('56469829', 'John', 'Smith');


--
-- TOC entry 4010 (class 0 OID 16483)
-- Dependencies: 207
-- Data for Name: customervehicles; Type: TABLE DATA; Schema: public; Owner: dbadmin
--

INSERT INTO public.customervehicles VALUES ('56473829', '902968876');
INSERT INTO public.customervehicles VALUES ('56437829', '901968876');
INSERT INTO public.customervehicles VALUES ('56469829', '701848734');

--
-- TOC entry 4006 (class 0 OID 16439)
-- Dependencies: 203
-- Data for Name: dealergeofences; Type: TABLE DATA; Schema: public; Owner: dbadmin
--

INSERT INTO public.dealergeofences VALUES ('geofence01', 'dealer01', NULL, '{
    "polygon": [
      [
        [
          -96.82403326034546,
          33.06841980033991
        ],
        [
          -96.8241834640503,
          33.06559658897117
        ],
        [
          -96.81877613067627,
          33.065686501557565
        ],
        [
          -96.81888341903687,
          33.06858163773721
        ],
        [
          -96.82403326034546,
          33.06841980033991
        ]
      ]
    ]
  }');
INSERT INTO public.dealergeofences VALUES ('geofence05', 'dealer05', NULL, '{
    "polygon": [
        [
          [
            -96.72154605388641,
            32.973293401748
          ],
          [
            -96.72155141830444,
            32.972136806571065
          ],
          [
            -96.72131538391113,
            32.972163808965774
          ],
          [
            -96.71961486339569,
            32.972136806571065
          ],
          [
            -96.71938419342041,
            32.9719162867053
          ],
          [
            -96.71898186206818,
            32.97175427175919
          ],
          [
            -96.71795725822447,
            32.973315903449496
          ],
          [
            -96.71830594539642,
            32.97345541387075
          ],
          [
            -96.7188638448715,
            32.973306902769586
          ],
          [
            -96.72154605388641,
            32.973293401748
          ]
        ]
      ]
  }');
INSERT INTO public.dealergeofences VALUES ('geofence02', 'dealer02', NULL, '{
    "polygon": [
      [
      ]
    ]
  }');
INSERT INTO public.dealergeofences VALUES ('geofence06', 'dealer06', NULL, '{
    "polygon": [
      [
      ]
    ]
  }');


--
-- TOC entry 4005 (class 0 OID 16436)
-- Dependencies: 202
-- Data for Name: dealers; Type: TABLE DATA; Schema: public; Owner: dbadmin
--

INSERT INTO public.dealers VALUES ('dealer01', 'Euro Calipso of Plano', '6800 Dallas Freeway', 'Plano', 'TX', '75024', 'USA', '(-96.820964,33.066461)', 'user@me.com', '2147046794');
INSERT INTO public.dealers VALUES ('dealer02', 'Voyager Cars of Dallas', '6200 Lemon Road', 'Dallas', 'TX', '75209', 'USA', '(-96.828737,32.834938)', 'user@me.com', '2147046794');
INSERT INTO public.dealers VALUES ('dealer03', 'Euro E-Trons of Grapevine', '1111 E State Hwy 114', 'Grapevine', 'TX', '76051', 'USA', '(-97.089423,32.924931)', 'suser@me.com', '2147046794');
INSERT INTO public.dealers VALUES ('dealer04', 'RoadCat Automotive of Arlington', '1105 E Lamar Blvd', 'Arlington', 'TX', '76011', 'USA', '(-97.0951834,32.7653086)', 'user@me.com', '2147046794');
INSERT INTO public.dealers VALUES ('dealer05', 'North Central Aura', '1819 N Central Expy', 'Richardson', 'TX', '75080', 'USA', '(-96.7189868,32.9717969)', 'user@me.com', '2147046794');
INSERT INTO public.dealers VALUES ('dealer06', 'AutoNation Maven Frisco', '6850 TX-121', 'Frisco', 'TX', '75034', 'USA', '(-96.8274878,33.0916296)', 'user@me.com', '2147046794');


--
-- TOC entry 4007 (class 0 OID 16442)
-- Dependencies: 204
-- Data for Name: dealervehicles; Type: TABLE DATA; Schema: public; Owner: dbadmin
--

INSERT INTO public.dealervehicles VALUES ('dealer01', '401869876');
INSERT INTO public.dealervehicles VALUES ('dealer01', '401869878');
INSERT INTO public.dealervehicles VALUES ('dealer05', '401848734');
INSERT INTO public.dealervehicles VALUES ('dealer05', '401866408');
INSERT INTO public.dealervehicles VALUES ('dealer06', '401849780');
INSERT INTO public.dealervehicles VALUES ('dealer02', '401968876');
INSERT INTO public.dealervehicles VALUES ('dealer04', '901968876');
INSERT INTO public.dealervehicles VALUES ('dealer04', '902968876');
INSERT INTO public.dealervehicles VALUES ('dealer05', '701848734');

--
-- TOC entry 4004 (class 0 OID 16415)
-- Dependencies: 201
-- Data for Name: vehicles; Type: TABLE DATA; Schema: public; Owner: dbadmin
--

INSERT INTO public.vehicles VALUES ('401869876', 'V30i 4dr Sedan (2.0L 4cyl Turbo 8A)', '8763b61e-2945-47ac-b3fb-bf16d4d316a6', '', 'Euro', '3 Series', 2021, 'mineral white', 'gas', 'sedan', 41250);
INSERT INTO public.vehicles VALUES ('401848734', 'XR 2dr Regular Cab 6.5 ft. SB (3.3L 6cyl 10A)', 'b4e2078b-2a1c-42ff-b8cc-5a66542698ca', '', 'Aura', 'X-150', 2021, 'race red', 'gas', 'truck', 28940);
INSERT INTO public.vehicles VALUES ('401849780', 'L Eco 4dr Hatchback (1.8L 4cyl gas/electric hybrid CVT)', '9c7306b5-d3b5-4662-abc0-cb3d03384837', '', 'RoadCat', 'Privy', 2021, 'strom blue', 'hybrid', 'hatchback', 24525);
INSERT INTO public.vehicles VALUES ('401869878', 'V340i xDrive 4dr Sedan AWD (3.0L 6cyl Turbo gas/electric hybrid 8A)', '6fe10fad-b1b5-49fa-a309-4b0550ad1d55', '', 'Euro', '3 Series', 2021, 'mettalic grey', 'gas', 'sedan', 56700);
INSERT INTO public.vehicles VALUES ('401866408', 'XLR 2dr Regular Cab 4WD 8 ft. LB (3.3L 6cyl 10A)', 'ebdb30ee-a2de-4b54-a1e3-2f6773ddcb01', '', 'Aura', 'X-150', 2021, 'oxford white', 'gas', 'sedan', 38775);
INSERT INTO public.vehicles VALUES ('401968876', 'V30i 4dr Sedan (2.0L 4cyl Turbo 8A)', '2a553b2c-0973-48e1-80ae-42427eabb290', '', 'Euro', '3 Series', 2021, 'mineral white', 'gas', 'sedan', 41250);
INSERT INTO public.vehicles VALUES ('902968876', 'V30i 4dr Sedan (2.0-liter BMW TwinPower Turbo inline 4-cylinder)', '62f10a51-d11d-42e2-aff8-99a502c90578', '', 'Euro', '5 Series', 2021, 'mineral white', 'gas', 'sedan', 41250);
INSERT INTO public.vehicles VALUES ('901968876', 'V30i 4dr Sedan (2.0-liter BMW TwinPower Turbo inline 4-cylinder)', 'b74e6b55-2de7-4910-aaec-444c8d721c36', '', 'Euro', '5 Series', 2021, 'mineral white', 'gas', 'sedan', 41250);
INSERT INTO public.vehicles VALUES ('701848734', 'Star SE (3.3L 6cyl 10A)', '12105196-733f-48ef-95d9-99ae6617cf50', '', 'Aura', 'Star', 2021, 'race red', 'gas', 'truck', 28940);
INSERT INTO public.vehicles VALUES ('702848734', 'XLT (turbocharged 2.3-liter four-cylinder)', '3563428e-7aed-4a0e-9b9d-e10181c0978f', '', 'Aura', 'Discover', 2022, 'race red', 'gas', 'SUV', 28940);


--
-- TOC entry 3863 (class 2606 OID 16490)
-- Name: customervehicles customers_pkey; Type: CONSTRAINT; Schema: public; Owner: dbadmin
--

ALTER TABLE ONLY public.customervehicles
    ADD CONSTRAINT customers_pkey PRIMARY KEY (customerid);


--
-- TOC entry 3865 (class 2606 OID 16539)
-- Name: customers customers_pkey1; Type: CONSTRAINT; Schema: public; Owner: dbadmin
--

ALTER TABLE ONLY public.customers
    ADD CONSTRAINT customers_pkey1 PRIMARY KEY (customerid);


--
-- TOC entry 3855 (class 2606 OID 16495)
-- Name: dealers dealers_pkey; Type: CONSTRAINT; Schema: public; Owner: dbadmin
--

ALTER TABLE ONLY public.dealers
    ADD CONSTRAINT dealers_pkey PRIMARY KEY (dealerid);


--
-- TOC entry 3857 (class 2606 OID 16570)
-- Name: dealervehicles dealervehicles_pkey; Type: CONSTRAINT; Schema: public; Owner: dbadmin
--

ALTER TABLE ONLY public.dealervehicles
    ADD CONSTRAINT dealervehicles_pkey PRIMARY KEY (vehicleid);


--
-- TOC entry 3861 (class 2606 OID 16531)
-- Name: geofenceevents geofenceevents_pkey; Type: CONSTRAINT; Schema: public; Owner: dbadmin
--

ALTER TABLE ONLY public.geofenceevents
    ADD CONSTRAINT geofenceevents_pkey PRIMARY KEY (eventid);


--
-- TOC entry 3853 (class 2606 OID 16424)
-- Name: vehicles vehicles_pkey; Type: CONSTRAINT; Schema: public; Owner: dbadmin
--

ALTER TABLE ONLY public.vehicles
    ADD CONSTRAINT vehicles_pkey PRIMARY KEY (vehicleid);


--
-- TOC entry 3859 (class 2606 OID 16497)
-- Name: vehiclestatus vehiclestatus_pkey; Type: CONSTRAINT; Schema: public; Owner: dbadmin
--

ALTER TABLE ONLY public.vehiclestatus
    ADD CONSTRAINT vehiclestatus_pkey PRIMARY KEY (vehicleid);


--
-- TOC entry 4019 (class 0 OID 0)
-- Dependencies: 4
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: dbadmin
--

REVOKE ALL ON SCHEMA public FROM rdsadmin;
REVOKE ALL ON SCHEMA public FROM PUBLIC;
GRANT ALL ON SCHEMA public TO dbadmin;
GRANT ALL ON SCHEMA public TO PUBLIC;


-- Completed on 2022-07-28 11:58:25 CDT

--
-- PostgreSQL database dump complete
--

