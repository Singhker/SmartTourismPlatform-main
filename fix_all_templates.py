import os

# Create templates folder if it doesn't exist
os.makedirs('templates', exist_ok=True)

# ============================================
# 1. curation.html
# ============================================
curation_content = '''{% extends "base.html" %}

{% block title %}Data Curation - Smart Tourism Platform{% endblock %}

{% block content %}
<div class="container py-4">
    <h2 class="mb-4"><i class="bi bi-brush"></i> Data Curation Dashboard</h2>

    <!-- Dataset Selector -->
    <div class="row mb-4">
        <div class="col-md-6">
            <form method="GET" class="d-flex gap-2">
                <select name="dataset" class="form-select" onchange="this.form.submit()">
                    {% for ds in datasets %}
                    <option value="{{ ds }}" {% if ds == selected %}selected{% endif %}>
                        {{ ds|replace('_', ' ')|title }}
                    </option>
                    {% endfor %}
                </select>
                <button type="submit" class="btn btn-primary">Load</button>
            </form>
        </div>
        <div class="col-md-6 text-end">
            <a href="{{ url_for('quality_report', dataset=selected) }}" class="btn btn-outline-info">
                <i class="bi bi-file-earmark-text"></i> Full Report
            </a>
        </div>
    </div>

    {% if report %}
    <div class="row mb-4">
        <div class="col-md-12">
            <div class="card shadow-sm border-0">
                <div class="card-body text-center">
                    <h3>Data Quality Score</h3>
                    <div class="display-1 fw-bold 
                        {% if report.quality_score >= 90 %}text-success
                        {% elif report.quality_score >= 75 %}text-primary
                        {% elif report.quality_score >= 60 %}text-warning
                        {% else %}text-danger{% endif %}">
                        {{ report.quality_score }}%
                    </div>
                    <h5><span class="badge bg-secondary">{{ report.quality_grade }}</span></h5>
                    <p class="text-muted">{{ report.total_rows }} rows, {{ report.total_columns }} columns</p>
                </div>
            </div>
        </div>
    </div>

    <div class="row g-4 mb-4">
        <div class="col-md-3">
            <div class="card shadow-sm border-0">
                <div class="card-body text-center">
                    <h6>Missing Values</h6>
                    <p class="display-6">{{ report.missing|sum }}</p>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card shadow-sm border-0">
                <div class="card-body text-center">
                    <h6>Duplicates</h6>
                    <p class="display-6">{{ report.duplicate_info.exact_duplicate_count }}</p>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card shadow-sm border-0">
                <div class="card-body text-center">
                    <h6>Valid Rows</h6>
                    <p class="display-6">{{ report.validation.valid_rows }}</p>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card shadow-sm border-0">
                <div class="card-body text-center">
                    <h6>Errors</h6>
                    <p class="display-6">{{ report.validation.errors|length }}</p>
                </div>
            </div>
        </div>
    </div>

    <div class="row mb-4">
        <div class="col-md-12">
            <div class="card shadow-sm border-0">
                <div class="card-body">
                    <h5>Apply Curation Fixes</h5>
                    <form method="POST" action="{{ url_for('curation_fix') }}" class="d-flex gap-3 flex-wrap">
                        <input type="hidden" name="dataset" value="{{ selected }}">
                        <button type="submit" name="operation" value="remove_duplicates" class="btn btn-warning">
                            <i class="bi bi-trash"></i> Remove Duplicates
                        </button>
                        <button type="submit" name="operation" value="handle_missing" class="btn btn-info">
                            <i class="bi bi-pencil"></i> Fill Missing Values
                        </button>
                        <button type="submit" name="operation" value="standardize" class="btn btn-success">
                            <i class="bi bi-check2"></i> Standardize Data
                        </button>
                    </form>
                </div>
            </div>
        </div>
    </div>

    <div class="row mb-4">
        <div class="col-md-12">
            <div class="card shadow-sm border-0">
                <div class="card-body">
                    <h5>Missing Values by Column</h5>
                    <div class="table-responsive">
                        <table class="table table-sm">
                            <thead>
                                <tr>
                                    <th>Column</th>
                                    <th>Missing Count</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for col, count in report.missing.items() %}
                                <tr>
                                    <td>{{ col }}</td>
                                    <td>{{ count }}</td>
                                    <td>
                                        {% if count > 0 %}
                                        <span class="badge bg-info">Need attention</span>
                                        {% else %}
                                        <span class="badge bg-success">Complete</span>
                                        {% endif %}
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>

    {% if report.validation.warnings %}
    <div class="row mb-4">
        <div class="col-md-12">
            <div class="card shadow-sm border-0">
                <div class="card-body">
                    <h5>Validation Warnings</h5>
                    <ul class="list-group">
                        {% for warning in report.validation.warnings %}
                        <li class="list-group-item list-group-item-warning">{{ warning }}</li>
                        {% endfor %}
                    </ul>
                </div>
            </div>
        </div>
    </div>
    {% endif %}

    {% if report.validation.errors %}
    <div class="row mb-4">
        <div class="col-md-12">
            <div class="card shadow-sm border-0">
                <div class="card-body">
                    <h5>Validation Errors</h5>
                    <ul class="list-group">
                        {% for error in report.validation.errors %}
                        <li class="list-group-item list-group-item-danger">{{ error }}</li>
                        {% endfor %}
                    </ul>
                </div>
            </div>
        </div>
    </div>
    {% endif %}

    {% else %}
    <div class="alert alert-info">
        <i class="bi bi-info-circle"></i> No data found or select a dataset to analyze.
    </div>
    {% endif %}
</div>
{% endblock %}'''

with open('templates/curation.html', 'w', encoding='utf-8') as f:
    f.write(curation_content)
print('✅ curation.html created')

# ============================================
# 2. recommendations.html
# ============================================
recommendations_content = '''{% extends "base.html" %}

{% block title %}Recommendations - Smart Tourism Platform{% endblock %}

{% block content %}
<div class="container py-4">
    <h2 class="mb-4"><i class="bi bi-star"></i> Place Recommendations</h2>
    <p class="text-muted">Find similar tourist places based on content and visitor preferences.</p>

    <div class="row mb-4">
        <div class="col-md-8">
            <div class="card shadow-sm border-0">
                <div class="card-body">
                    <form method="GET" class="row g-3">
                        <div class="col-md-8">
                            <label for="place_id" class="form-label">Select a Tourist Place</label>
                            <select name="place_id" id="place_id" class="form-select" required>
                                <option value="">-- Select a place --</option>
                                {% for place in places %}
                                <option value="{{ place.place_id }}" {% if place.place_id == selected_place %}selected{% endif %}>
                                    {{ place.place_name }}
                                </option>
                                {% endfor %}
                            </select>
                        </div>
                        <div class="col-md-4 d-flex align-items-end">
                            <button type="submit" class="btn btn-primary w-100">
                                <i class="bi bi-search"></i> Find Similar
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card shadow-sm border-0 bg-light">
                <div class="card-body text-center">
                    <h6 class="text-muted">How it works</h6>
                    <small>
                        Using content-based filtering, the system compares 
                        place descriptions, categories, districts, and 
                        features to find the most similar tourist 
                        attractions.
                    </small>
                </div>
            </div>
        </div>
    </div>

    {% if selected_place %}
        {% if recommendations and recommendations|length > 0 %}
            <div class="row mb-4">
                <div class="col-md-12">
                    <h4>Similar Places</h4>
                    <p class="text-muted">Showing {{ recommendations|length }} recommendations</p>
                </div>
            </div>

            <div class="row g-4">
                {% for rec in recommendations %}
                <div class="col-md-4">
                    <div class="card h-100 shadow-sm border-0">
                        <div class="card-body">
                            <h5 class="card-title">{{ rec.place_name }}</h5>
                            <p class="card-text small text-muted">
                                <span class="badge bg-primary">{{ rec.place_id }}</span>
                            </p>
                            <div class="mb-2">
                                <span class="badge bg-success">Similarity: {{ "%.2f"|format(rec.similarity_score|default(0)) }}</span>
                            </div>
                            <a href="{{ url_for('place_detail', place_id=rec.place_id) }}" class="btn btn-outline-primary btn-sm">
                                <i class="bi bi-eye"></i> View Details
                            </a>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>

        {% else %}
            <div class="row">
                <div class="col-md-12">
                    <div class="alert alert-warning">
                        <i class="bi bi-exclamation-triangle"></i> 
                        No similar places found for the selected location.
                    </div>
                </div>
            </div>
        {% endif %}
    {% else %}
        <div class="row">
            <div class="col-md-12">
                <div class="alert alert-info">
                    <i class="bi bi-info-circle"></i> 
                    Select a tourist place from the dropdown above to get recommendations.
                </div>
            </div>
        </div>
    {% endif %}

    <div class="row mt-4">
        <div class="col-md-12">
            <a href="{{ url_for('places') }}" class="btn btn-outline-secondary">
                <i class="bi bi-arrow-left"></i> Browse All Places
            </a>
        </div>
    </div>
</div>
{% endblock %}'''

with open('templates/recommendations.html', 'w', encoding='utf-8') as f:
    f.write(recommendations_content)
print('✅ recommendations.html created')

# ============================================
# 3. quality_report.html
# ============================================
quality_report_content = '''{% extends "base.html" %}

{% block title %}Quality Report - Smart Tourism Platform{% endblock %}

{% block content %}
<div class="container py-4">
    <h2 class="mb-4"><i class="bi bi-file-earmark-text"></i> Quality Report</h2>
    <p class="text-muted">
        Dataset: <strong>{{ dataset|replace('_', ' ')|title }}</strong>
        <span class="badge bg-secondary ms-2">{{ report.total_rows if report else 0 }} rows</span>
    </p>

    {% if report %}
    <div class="row g-4 mb-4">
        <div class="col-md-12">
            <div class="card shadow-sm border-0">
                <div class="card-body text-center py-5">
                    <h3>Overall Data Quality</h3>
                    <div class="display-1 fw-bold 
                        {% if report.quality_score >= 90 %}text-success
                        {% elif report.quality_score >= 75 %}text-primary
                        {% elif report.quality_score >= 60 %}text-warning
                        {% else %}text-danger{% endif %}">
                        {{ report.quality_score }}%
                    </div>
                    <h4><span class="badge bg-secondary">{{ report.quality_grade }}</span></h4>
                    <p class="text-muted">{{ report.total_rows }} rows · {{ report.total_columns }} columns</p>
                </div>
            </div>
        </div>
    </div>

    <div class="row g-4 mb-4">
        <div class="col-md-3">
            <div class="card shadow-sm border-0">
                <div class="card-body text-center">
                    <h6 class="text-muted">Total Rows</h6>
                    <p class="display-6">{{ report.total_rows }}</p>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card shadow-sm border-0">
                <div class="card-body text-center">
                    <h6 class="text-muted">Missing Values</h6>
                    <p class="display-6">{{ report.missing|sum }}</p>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card shadow-sm border-0">
                <div class="card-body text-center">
                    <h6 class="text-muted">Duplicates</h6>
                    <p class="display-6">{{ report.duplicate_info.exact_duplicate_count }}</p>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card shadow-sm border-0">
                <div class="card-body text-center">
                    <h6 class="text-muted">Valid Rows</h6>
                    <p class="display-6">{{ report.validation.valid_rows }}</p>
                </div>
            </div>
        </div>
    </div>

    <div class="row g-4 mb-4">
        <div class="col-md-6">
            <div class="card shadow-sm border-0">
                <div class="card-body">
                    <h5><i class="bi bi-info-circle"></i> Dataset Info</h5>
                    <table class="table table-sm table-borderless">
                        <tr><th>Name</th><td>{{ dataset|replace('_', ' ')|title }}</td></tr>
                        <tr><th>Total Columns</th><td>{{ report.total_columns }}</td></tr>
                        <tr><th>Total Rows</th><td>{{ report.total_rows }}</td></tr>
                        <tr><th>Quality Score</th>
                            <td>
                                <span class="badge 
                                    {% if report.quality_score >= 90 %}bg-success
                                    {% elif report.quality_score >= 75 %}bg-primary
                                    {% elif report.quality_score >= 60 %}bg-warning
                                    {% else %}bg-danger{% endif %}">
                                    {{ report.quality_score }}%
                                </span>
                            </td>
                        </tr>
                    </table>
                </div>
            </div>
        </div>
        <div class="col-md-6">
            <div class="card shadow-sm border-0">
                <div class="card-body">
                    <h5><i class="bi bi-list-columns"></i> Columns</h5>
                    <div style="max-height:300px;overflow-y:auto;">
                        <ul class="list-unstyled">
                            {% for col in report.columns %}
                            <li>
                                <span class="badge bg-light text-dark">{{ col }}</span>
                                <small class="text-muted">({{ report.dtypes[col] }})</small>
                                {% if report.missing[col] > 0 %}
                                <span class="badge bg-warning text-dark">missing: {{ report.missing[col] }}</span>
                                {% endif %}
                            </li>
                            {% endfor %}
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="row g-4 mb-4">
        <div class="col-md-12">
            <div class="card shadow-sm border-0">
                <div class="card-body">
                    <h5><i class="bi bi-exclamation-triangle"></i> Missing Values by Column</h5>
                    <div class="table-responsive">
                        <table class="table table-sm table-hover">
                            <thead>
                                <tr>
                                    <th>Column</th>
                                    <th>Missing Count</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for col in report.columns %}
                                <tr>
                                    <td>{{ col }}</td>
                                    <td>{{ report.missing[col] }}</td>
                                    <td>
                                        {% if report.missing[col] == 0 %}
                                        <span class="badge bg-success">Complete</span>
                                        {% elif report.missing[col] <= 5 %}
                                        <span class="badge bg-warning text-dark">Minor</span>
                                        {% else %}
                                        <span class="badge bg-danger">Critical</span>
                                        {% endif %}
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="row g-4 mb-4">
        <div class="col-md-6">
            <div class="card shadow-sm border-0">
                <div class="card-body">
                    <h5><i class="bi bi-x-circle text-danger"></i> Validation Errors</h5>
                    {% if report.validation.errors %}
                    <ul class="list-group">
                        {% for error in report.validation.errors %}
                        <li class="list-group-item list-group-item-danger">{{ error }}</li>
                        {% endfor %}
                    </ul>
                    {% else %}
                    <p class="text-success"><i class="bi bi-check-circle"></i> No validation errors found.</p>
                    {% endif %}
                </div>
            </div>
        </div>
        <div class="col-md-6">
            <div class="card shadow-sm border-0">
                <div class="card-body">
                    <h5><i class="bi bi-exclamation-circle text-warning"></i> Validation Warnings</h5>
                    {% if report.validation.warnings %}
                    <ul class="list-group">
                        {% for warning in report.validation.warnings %}
                        <li class="list-group-item list-group-item-warning">{{ warning }}</li>
                        {% endfor %}
                    </ul>
                    {% else %}
                    <p class="text-success"><i class="bi bi-check-circle"></i> No validation warnings.</p>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>

    <div class="row g-4">
        <div class="col-md-12">
            <div class="card shadow-sm border-0">
                <div class="card-body">
                    <h5>Actions</h5>
                    <div class="d-flex gap-3 flex-wrap">
                        <a href="{{ url_for('curation', dataset=dataset) }}" class="btn btn-primary">
                            <i class="bi bi-brush"></i> Open Curation Dashboard
                        </a>
                        <a href="{{ url_for('places') }}" class="btn btn-outline-secondary">
                            <i class="bi bi-arrow-left"></i> Back to Places
                        </a>
                        <button onclick="window.print()" class="btn btn-outline-info">
                            <i class="bi bi-printer"></i> Print Report
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    {% else %}
    <div class="alert alert-warning">
        <i class="bi bi-exclamation-triangle"></i> No quality report available. 
        <a href="{{ url_for('curation') }}" class="alert-link">Go to Curation</a> to generate a report.
    </div>
    {% endif %}
</div>
{% endblock %}'''

with open('templates/quality_report.html', 'w', encoding='utf-8') as f:
    f.write(quality_report_content)
print('✅ quality_report.html created')

print('')
print('=' * 50)
print('✅ ALL TEMPLATES CREATED SUCCESSFULLY!')
print('=' * 50)
print('')
print('Now restart Flask: python app.py')
print('Then test:')
print('  - http://127.0.0.1:5000/recommendations')
print('  - http://127.0.0.1:5000/curation')
print('  - http://127.0.0.1:5000/quality-report?dataset=tourist_places')
