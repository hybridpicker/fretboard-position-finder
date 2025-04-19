#!/bin/bash
# SEO Implementation Test Script for Guitar Fretboard Position Finder

echo "Starting SEO Implementation Tests..."
echo "===================================="

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "Virtual environment activated"
fi

# Run the Django test for SEO implementation
python manage.py test positionfinder.tests_seo

# Check for template syntax errors
echo ""
echo "Checking for template syntax errors..."
python manage.py validate_templates

# Run checks for the single-page application structure
echo ""
echo "Verifying single-page app SEO setup..."

# Check if key files exist
echo "Checking for key SEO files..."
key_files=("templates/fretboardbase.html" 
           "templates/seo/chord_structured_data.html"
           "templates/seo/scale_structured_data.html"
           "templates/seo/arpeggio_structured_data.html"
           "positionfinder/seo_context_processor.py"
           "static/robots.txt")
           
files_found=0
total_files=${#key_files[@]}

for file in "${key_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✓ Found: $file"
        files_found=$((files_found+1))
    else
        echo "✗ Missing: $file"
    fi
done

echo "$files_found out of $total_files key files found."

# Check for JSON-LD in structured data templates
echo ""
echo "Validating structured data..."

for template in templates/seo/*.html; do
    if grep -q 'application/ld+json' "$template"; then
        echo "✓ $template contains JSON-LD structured data"
    else
        echo "✗ $template is missing JSON-LD structured data"
    fi
done

# Check meta tags in base template
echo ""
echo "Checking metadata in base template..."
base_template="templates/fretboardbase.html"
meta_found=0
total_meta=8

if grep -q 'meta name="description"' "$base_template"; then
    echo "✓ Meta description found"
    meta_found=$((meta_found+1))
else
    echo "✗ Meta description missing"
fi

if grep -q 'meta name="keywords"' "$base_template"; then
    echo "✓ Meta keywords found"
    meta_found=$((meta_found+1))
else
    echo "✗ Meta keywords missing"
fi

if grep -q 'property="og:title"' "$base_template"; then
    echo "✓ Open Graph title found"
    meta_found=$((meta_found+1))
else
    echo "✗ Open Graph title missing"
fi

if grep -q 'property="og:description"' "$base_template"; then
    echo "✓ Open Graph description found"
    meta_found=$((meta_found+1))
else
    echo "✗ Open Graph description missing"
fi

if grep -q 'name="twitter:title"' "$base_template"; then
    echo "✓ Twitter card title found"
    meta_found=$((meta_found+1))
else
    echo "✗ Twitter card title missing"
fi

if grep -q 'name="twitter:description"' "$base_template"; then
    echo "✓ Twitter card description found"
    meta_found=$((meta_found+1))
else
    echo "✗ Twitter card description missing"
fi

if grep -q 'application/ld+json' "$base_template"; then
    echo "✓ Structured data found"
    meta_found=$((meta_found+1))
else
    echo "✗ Structured data missing"
fi

if grep -q 'canonical' "$base_template"; then
    echo "✓ Canonical URL found"
    meta_found=$((meta_found+1))
else
    echo "✗ Canonical URL missing"
fi

echo ""
echo "Found $meta_found out of $total_meta expected meta tags"
if [ $meta_found -eq $total_meta ]; then
    echo "✓ All metadata tags are present"
else
    echo "✗ Some metadata tags are missing"
fi

# Check if context processor is registered
echo ""
echo "Checking context processor registration..."
settings_file="fretboard/settings.py"

if grep -q "seo_context_processor.get_seo_metadata" "$settings_file"; then
    echo "✓ SEO context processor is registered in settings.py"
else
    echo "✗ SEO context processor is NOT registered in settings.py"
fi

# Check robots.txt
echo ""
echo "Checking robots.txt content..."
robots_file="static/robots.txt"

if grep -q "User-agent: \*" "$robots_file" && grep -q "Allow: /" "$robots_file" && grep -q "Disallow: /admin/" "$robots_file" && grep -q "Sitemap:" "$robots_file"; then
    echo "✓ robots.txt contains all required directives"
else
    echo "✗ robots.txt is missing required directives"
fi

# Calculate overall score
echo ""
echo "SEO Implementation Score:"
echo "--------------------------"
total_score=$((files_found + meta_found))
total_possible=$((total_files + total_meta))
score_percent=$((total_score * 100 / total_possible))

echo "Score: $score_percent% ($total_score out of $total_possible points)"

# Suggest next steps based on score
echo ""
echo "Recommendations:"
if [ $score_percent -eq 100 ]; then
    echo "✅ Excellent! Your SEO implementation is complete."
    echo "Next steps:"
    echo "  - Run the URL checker tool on your live site: python check_url_seo.py http://localhost:8000/"
    echo "  - Consider adding more detailed structured data for your musical content"
    echo "  - Monitor search engine rankings after deployment"
elif [ $score_percent -ge 80 ]; then
    echo "👍 Good job! Your SEO implementation is mostly complete."
    echo "Next steps:"
    echo "  - Address the missing items identified above"
    echo "  - Run the URL checker tool to verify the implementation"
else
    echo "⚠️ Your SEO implementation needs work."
    echo "Next steps:"
    echo "  - Focus on implementing the missing components identified above"
    echo "  - Re-run this test after fixing the issues"
fi

echo ""
echo "SEO Implementation Tests Completed"
echo "=================================="
