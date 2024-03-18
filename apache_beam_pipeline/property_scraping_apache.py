import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, GoogleCloudOptions

# Define pipeline options
options = PipelineOptions()
google_cloud_options = options.view_as(GoogleCloudOptions)
google_cloud_options.project = 'scrapercloudrun'  # Update project ID here
google_cloud_options.job_name = 'property-scraping-dataflow'
google_cloud_options.staging_location = 'gs://real_estate_scraping/stage_files'  # Update staging location
google_cloud_options.temp_location = 'gs://real_estate_scraping/temp_files'  # Update temp location

# Define the BigQuery table schema
table_schema = {
    'fields': [
        {'name': 'street', 'type': 'STRING'},
        {'name': 'title', 'type': 'STRING'},
        {'name': 'type', 'type': 'STRING'},
        {'name': 'size', 'type': 'STRING'},
        {'name': 'current_datetime', 'type': 'STRING'}
    ]
}

# Define the pipeline
with beam.Pipeline(options=options) as pipeline:
    # Read data from CSV file in Google Cloud Storage
    lines = (
        pipeline
        | 'ReadFromCSV' >> beam.io.ReadFromText('gs://real_estate_scraping/bratislava/scrape-2024-03-14_23-26-23.csv')
    )

    # Write data to BigQuery
    _ = (
        lines
        | 'WriteToBigQuery' >> beam.io.WriteToBigQuery(
            table='real-estate-scraper:scrapercloudrun.property_scraped',
            schema=table_schema,
            create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
            write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND)
    )
