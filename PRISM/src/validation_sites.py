"""
PRISM -- independent ice-reference site table.

Sources (all real, cited, non-PRISM):
  - Colaprete et al. (2010), "Detection of water in the LCROSS ejecta plume,"
    Science 330(6003):463-468, doi:10.1126/science.1186986 -- direct in-situ
    plume spectroscopy, ~5.6 wt% H2O in the Cabeus ejecta. This is the single
    highest-confidence independent ice detection available for this project.
  - Marshall et al. (2011), "Locating the LCROSS Impact Craters," Space
    Science Reviews, doi:10.1007/s11214-011-9765-0 -- precise Centaur impact
    coordinate: -84.6796 deg lat, -48.7093 deg lon (311.2907 deg E), 1-sigma
    uncertainty 115 m (lat) / 44 m (lon).
  - Li, S. et al. (2018), "Direct evidence of surface exposed water ice in
    the lunar polar regions," PNAS 115(36):8907-8912,
    doi:10.1073/pnas.1802345115 -- M3 3-micron ice-absorption-feature
    detections. The paper's own text and SI Appendix (Fig. S5) name specific
    craters with positive detections and specific craters checked but
    NEGATIVE (no ice exposure found) -- both used here. IMPORTANT: the
    paper's actual ice-detection data is a per-pixel (~280x280 m) MAP
    overlaid on a Diviner temperature figure (SI Fig. S5) -- there is NO
    machine-readable coordinate table of individual ice-bearing M3 pixels in
    the main text or the 23-page SI Appendix (verified this session by
    extracting and full-text-searching the actual SI PDF, downloaded from
    Europe PMC: outputs/validation/refs/pnas.1802345115.sapp.pdf -- Table S1
    in that document is spectral absorption-band wavelength characteristics,
    NOT a coordinate list). What IS available and used here is CRATER-LEVEL:
    the named craters where the paper reports ice was / was not detected
    somewhere within the crater. This is a real limitation, documented in
    docs/INDEPENDENT_ICE_VALIDATION.md, not a substitute for pixel-level data.
  - Crater center coordinates and diameters: USGS Gazetteer of Planetary
    Nomenclature (planetarynames.wr.usgs.gov), the official IAU-approved
    lunar nomenclature database, reproduced via each crater's Wikipedia
    infobox (which cites the Gazetteer directly) since the Gazetteer's own
    search endpoint returned server errors this session. NOT from Li et al.
    2018 or from any PRISM output.

CRITICAL: crater CENTER coordinates are a proxy for "somewhere in this
crater," not the exact M3 ice-pixel location. Window size is scaled to each
crater's own radius (see validation_pipeline.py) specifically to reduce (not
eliminate) this mismatch.
"""

SITES = [
    # --- POSITIVE: independently identified/confirmed ice ---
    dict(site_id="LCROSS_Cabeus", name="LCROSS Centaur impact site (Cabeus)",
         category="positive", lat=-84.6796, lon=-48.7093, diameter_km=None,
         window_half_km=1.0,  # small: this is a point plume-spectroscopy measurement, not a crater-scale detection
         region="south",
         source_mission="LCROSS (LCROSS/Centaur upper stage impactor)",
         source_publication="Colaprete et al. 2010, Science 330(6003):463-468, doi:10.1126/science.1186986; location per Marshall et al. 2011, Space Science Reviews, doi:10.1007/s11214-011-9765-0",
         evidence_type="Direct in-situ UV-vis/NIR spectroscopy of impact ejecta plume, ~5.6 wt% H2O detected",
         confidence="HIGH -- direct sample, not remote spectral inference",
         coordinate_source="Marshall et al. 2011 (impact-point-specific, 1-sigma ~115m lat / 44m lon)"),
    dict(site_id="Faustini", name="Faustini", category="positive",
         lat=-87.3, lon=77.0, diameter_km=39.0, window_half_km=19.5, region="south",
         source_mission="Chandrayaan-1 Moon Mineralogy Mapper (M3)",
         source_publication="Li et al. 2018, PNAS 115(36):8907-8912, doi:10.1073/pnas.1802345115",
         evidence_type="M3 3-micron ice absorption feature (remote reflectance spectroscopy), crater-level (see module docstring)",
         confidence="MODERATE -- remote spectral inference, criterion itself has published scientific critique (see docs)",
         coordinate_source="USGS Gazetteer of Planetary Nomenclature via Wikipedia infobox"),
    dict(site_id="De_Gerlache", name="de Gerlache", category="positive",
         lat=-88.5, lon=-87.1, diameter_km=32.4, window_half_km=16.2, region="south",
         source_mission="Chandrayaan-1 M3", source_publication="Li et al. 2018, PNAS 115(36):8907-8912",
         evidence_type="M3 3-micron ice absorption feature, crater-level",
         confidence="MODERATE", coordinate_source="USGS Gazetteer via Wikipedia infobox"),
    dict(site_id="Haworth", name="Haworth", category="positive",
         lat=-86.9, lon=-4.0, diameter_km=51.4, window_half_km=25.7, region="south",
         source_mission="Chandrayaan-1 M3", source_publication="Li et al. 2018, PNAS 115(36):8907-8912",
         evidence_type="M3 3-micron ice absorption feature, crater-level",
         confidence="MODERATE", coordinate_source="USGS Gazetteer via Wikipedia infobox"),
    dict(site_id="Shoemaker", name="Shoemaker", category="positive",
         lat=-88.1, lon=44.9, diameter_km=50.9, window_half_km=25.5, region="south",
         source_mission="Chandrayaan-1 M3", source_publication="Li et al. 2018, PNAS 115(36):8907-8912",
         evidence_type="M3 3-micron ice absorption feature, crater-level",
         confidence="MODERATE", coordinate_source="USGS Gazetteer via Wikipedia infobox"),
    dict(site_id="Sverdrup", name="Sverdrup", category="positive",
         lat=-88.5, lon=-152.0, diameter_km=35.0, window_half_km=17.5, region="south",
         source_mission="Chandrayaan-1 M3", source_publication="Li et al. 2018, PNAS 115(36):8907-8912",
         evidence_type="M3 3-micron ice absorption feature, crater-level",
         confidence="MODERATE", coordinate_source="USGS Gazetteer via Wikipedia infobox"),
    dict(site_id="Shackleton", name="Shackleton", category="positive",
         lat=-89.67, lon=129.78, diameter_km=21.0, window_half_km=10.5, region="south",
         source_mission="Chandrayaan-1 M3", source_publication="Li et al. 2018, PNAS 115(36):8907-8912",
         evidence_type="M3 3-micron ice absorption feature, crater-level",
         confidence="MODERATE", coordinate_source="USGS Gazetteer via Wikipedia infobox"),
    dict(site_id="Rozhdestvenskiy", name="Rozhdestvenskiy", category="positive",
         lat=85.2, lon=-155.4, diameter_km=177.0, window_half_km=88.5, region="north",
         source_mission="Chandrayaan-1 M3", source_publication="Li et al. 2018, PNAS 115(36):8907-8912",
         evidence_type="M3 3-micron ice absorption feature, crater-level",
         confidence="MODERATE", coordinate_source="USGS Gazetteer via Wikipedia infobox",
         notes="NORTH POLE -- outside PRISM's south-polar Y4R/CPR mosaic and LOLA-PSR-catalog coverage."),

    # --- CONTROL: comparable locations, explicitly checked and reported as
    #     NOT showing ice exposure in Li et al. 2018 (not merely "unstudied") ---
    dict(site_id="Amundsen", name="Amundsen", category="control",
         lat=-84.5, lon=82.8, diameter_km=103.39, window_half_km=51.7, region="south",
         source_mission="Chandrayaan-1 M3 (checked, negative) / Diviner (cold trap)",
         source_publication="Li et al. 2018, PNAS 115(36):8907-8912 (SI Appendix Fig. S5: 'cold traps not showing ice exposures')",
         evidence_type="Cold trap (Diviner Tmax <=110K) explicitly checked for M3 ice absorption -- NOT detected",
         confidence="Source explicitly reports NO ice exposure (not merely unstudied)",
         coordinate_source="USGS Gazetteer via Wikipedia infobox"),
    dict(site_id="Hedervari", name="Hedervari", category="control",
         lat=-81.8, lon=84.0, diameter_km=69.0, window_half_km=34.5, region="south",
         source_mission="Chandrayaan-1 M3 (checked, negative) / Diviner (cold trap)",
         source_publication="Li et al. 2018, PNAS 115(36):8907-8912 (SI Appendix Fig. S5)",
         evidence_type="Cold trap explicitly checked for M3 ice absorption -- NOT detected",
         confidence="Source explicitly reports NO ice exposure",
         coordinate_source="USGS Gazetteer via Wikipedia infobox"),
    dict(site_id="Idelson_L", name="Idel'son L", category="control",
         lat=-84.2, lon=115.8, diameter_km=28.0, window_half_km=14.0, region="south",
         source_mission="Chandrayaan-1 M3 (checked, negative) / Diviner (cold trap)",
         source_publication="Li et al. 2018, PNAS 115(36):8907-8912 (SI Appendix Fig. S5)",
         evidence_type="Cold trap explicitly checked for M3 ice absorption -- NOT detected",
         confidence="Source explicitly reports NO ice exposure",
         coordinate_source="USGS Gazetteer via Wikipedia infobox (satellite-crater table)"),
    dict(site_id="Wiechert", name="Wiechert", category="control",
         lat=-84.5, lon=165.0, diameter_km=41.0, window_half_km=20.5, region="south",
         source_mission="Chandrayaan-1 M3 (checked, negative) / Diviner (cold trap)",
         source_publication="Li et al. 2018, PNAS 115(36):8907-8912 (SI Appendix Fig. S5)",
         evidence_type="Cold trap explicitly checked for M3 ice absorption -- NOT detected",
         confidence="Source explicitly reports NO ice exposure",
         coordinate_source="USGS Gazetteer via Wikipedia infobox"),
    dict(site_id="Bosch", name="Bosch", category="control",
         lat=86.82, lon=133.6, diameter_km=19.58, window_half_km=9.79, region="north",
         source_mission="Chandrayaan-1 M3 (checked, negative) / Diviner (cold trap)",
         source_publication="Li et al. 2018, PNAS 115(36):8907-8912 (SI Appendix Fig. S5)",
         evidence_type="Cold trap explicitly checked for M3 ice absorption -- NOT detected",
         confidence="Source explicitly reports NO ice exposure",
         coordinate_source="USGS Gazetteer via Wikipedia infobox",
         notes="NORTH POLE -- outside PRISM's south-polar Y4R/CPR mosaic and LOLA-PSR-catalog coverage."),
]

for s in SITES:
    s.setdefault("notes", "")
