# Data Directory

This directory is for storing test datasets and sample documents for PII detection validation.

## Structure

```
data/
├── Structured Data (PDF)/          # PDF documents with known PII
└── Unstructured Data & Supplementary Identifiers/  # Images and other formats
```

## Usage

1. Place sample PDF documents in the `Structured Data (PDF)/` folder
2. Add test images and other document formats in the `Unstructured Data & Supplementary Identifiers/` folder
3. Use these files to test and validate the PII detection accuracy

## Sample Data Sources

- Healthcare records (anonymized)
- Legal documents (redacted)
- Financial statements (sample data)
- Government forms (public templates)

**Note**: Ensure all test data complies with privacy regulations and does not contain actual sensitive information.