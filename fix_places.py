import os
content = '''{% extends "base.html" %}

{% block title %}Tourist Places - Smart Tourism Platform{% endblock %}

{% block content %}
<div class="container py-4">
    <div class="row mb-4">
        <div class="col-12">
            <h1 class="display-5 fw-bold text-primary">
                <i class="bi bi-geo-alt-fill"></i> Tourist Places in Manipur
            </h1>
            <p class="text-muted">Discover the beautiful destinations of Manipur</p>
            <hr>
        </div>
    </div>

    <div class="card shadow-sm mb-4 border-0">
        <div class="card-body">
            <form method="GET" class="row g-3 align-items-end">
                <div class="col-md-4">
                    <label class="form-label fw-semibold">
                        <i class="bi bi-search"></i> Search
                    </label>
                    <input type="text" name="search" class="form-control" placeholder="Search by name..." value="{{ search or '' }}">
                </div>

                <div class="col-md-3">
                    <label class="form-label fw-semibold">
                        <i class="bi bi-building"></i> District
                    </label>
                    <select name="district" class="form-select">
                        <option value="">All Districts</option>
                        {% for d in districts %}
                        <option value="{{ d }}" {% if d == district %}selected{% endif %}>{{ d }}</option>
                        {% endfor %}
                    </select>
                </div>

                <div class="col-md-3">
                    <label class="form-label fw-semibold">
                        <i class="bi bi-tag"></i> Category
                    </label>
                    <select name="category" class="form-select">
                        <option value="">All Categories</option>
                        {% for c in categories %}
                        <option value="{{ c }}" {% if c == category %}selected{% endif %}>{{ c }}</option>
                        {% endfor %}
                    </select>
                </div>

                <div class="col-md-2">
                    <button type="submit" class="btn btn-primary w-100">
                        <i class="bi bi-funnel"></i> Filter
                    </button>
                    <a href="{{ url_for('places') }}" class="btn btn-outline-secondary w-100 mt-1">
                        <i class="bi bi-arrow-counterclockwise"></i> Clear
                    </a>
                </div>
            </form>
        </div>
    </div>

    <div class="row mb-3">
        <div class="col-12">
            <p class="text-muted">
                <i class="bi bi-info-circle"></i>
                Showing <strong>{{ places|length }}</strong> places
            </p>
        </div>
    </div>

    {% if places %}
    <div class="row g-4">
        {% for place in places %}
        <div class="col-md-6 col-lg-4">
            <div class="card h-100 shadow-sm border-0 hover-card">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <h5 class="card-title fw-bold text-primary mb-0">
                            {{ place.place_name }}
                        </h5>
                        <span class="badge bg-primary rounded-pill">{{ place.popularity_level }}</span>
                    </div>

                    <p class="text-muted small mb-2">
                        <i class="bi bi-geo-alt"></i> {{ place.district }}
                        <span class="mx-1">•</span>
                        <i class="bi bi-tag"></i> {{ place.category }}
                    </p>

                    <p class="card-text text-secondary small">
                        {{ place.description[:100] }}...
                    </p>

                    <div class="mb-2 d-flex flex-wrap gap-1">
                        {% if place.family_friendly == 'Yes' %}
                        <span class="badge bg-success"><i class="bi bi-people"></i> Family</span>
                        {% endif %}
                        {% if place.adventure_level == 'High' %}
                        <span class="badge bg-danger"><i class="bi bi-mountain"></i> Adventure</span>
                        {% endif %}
                        <span class="badge bg-info"><i class="bi bi-calendar"></i> {{ place.best_season }}</span>
                        {% if place.entry_fee_inr > 0 %}
                        <span class="badge bg-warning text-dark">₹{{ place.entry_fee_inr }}</span>
                        {% else %}
                        <span class="badge bg-secondary">Free Entry</span>
                        {% endif %}
                    </div>

                    <div class="mt-2 d-flex justify-content-between align-items-center">
                        <div>
                            {% if place.opening_time and place.opening_time != 'Open All Day' %}
                            <small class="text-muted">
                                <i class="bi bi-clock"></i> {{ place.opening_time }}
                            </small>
                            {% endif %}
                        </div>
                        <a href="{{ url_for('place_detail', place_id=place.place_id) }}" class="btn btn-outline-primary btn-sm">
                            <i class="bi bi-eye"></i> View Details
                        </a>
                    </div>
                </div>
            </div>
        </div>
        {% endfor %}
    </div>
    {% else %}
    <div class="alert alert-info text-center py-5">
        <i class="bi bi-search display-4 d-block mb-3"></i>
        <h4>No places found</h4>
        <p class="text-muted">Try adjusting your search or filter criteria</p>
    </div>
    {% endif %}

    {% if pages and pages > 1 %}
    <nav class="mt-4">
        <ul class="pagination justify-content-center">
            <li class="page-item {% if page == 1 %}disabled{% endif %}">
                <a class="page-link" href="?page={{ page - 1 }}{% if search %}&search={{ search }}{% endif %}{% if district %}&district={{ district }}{% endif %}{% if category %}&category={{ category }}{% endif %}">
                    <i class="bi bi-chevron-left"></i>
                </a>
            </li>
            {% for p in range(1, pages + 1) %}
            <li class="page-item {% if p == page %}active{% endif %}">
                <a class="page-link" href="?page={{ p }}{% if search %}&search={{ search }}{% endif %}{% if district %}&district={{ district }}{% endif %}{% if category %}&category={{ category }}{% endif %}">
                    {{ p }}
                </a>
            </li>
            {% endfor %}
            <li class="page-item {% if page == pages %}disabled{% endif %}">
                <a class="page-link" href="?page={{ page + 1 }}{% if search %}&search={{ search }}{% endif %}{% if district %}&district={{ district }}{% endif %}{% if category %}&category={{ category }}{% endif %}">
                    <i class="bi bi-chevron-right"></i>
                </a>
            </li>
        </ul>
    </nav>
    {% endif %}
</div>

<style>
.hover-card {
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.hover-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.15) !important;
}
.badge {
    font-weight: 500;
    padding: 4px 10px;
}
</style>
{% endblock %}'''

os.makedirs('templates', exist_ok=True)
with open('templates/places.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('✅ places.html created successfully!')
print('📁 File location: templates/places.html')
print('📊 File size:', len(content), 'characters')
