from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from database.db import query_db
from backend.services.agmarknet_service import AgmarknetService

mandi_bp = Blueprint('mandi', __name__, url_prefix='/mandi')

@mandi_bp.route('/prices')
def prices():
    state = request.args.get('state', 'All')
    district = request.args.get('district', 'All')
    crop_name = request.args.get('crop', 'All')
    search = request.args.get('q', '').strip()

    filter_opts = AgmarknetService.get_filter_options()
    prices_list = AgmarknetService.get_prices(
        state=state if state != 'All' else None,
        district=district if district != 'All' else None,
        crop_name=crop_name if crop_name != 'All' else (search if search else None),
        limit=100
    )

    # Average modal price statistics for top crops
    top_stats = query_db(
        """SELECT crop_name, ROUND(AVG(modal_price), 2) as avg_price, 
                  MIN(min_price) as lowest, MAX(max_price) as highest, COUNT(*) as count 
           FROM market_prices 
           GROUP BY crop_name 
           ORDER BY count DESC LIMIT 6"""
    )

    latest_date_row = query_db("SELECT MAX(price_date) as max_date FROM market_prices", one=True)
    latest_update = latest_date_row['max_date'] if latest_date_row and latest_date_row['max_date'] else 'Today'

    return render_template(
        'mandi/prices.html',
        prices=prices_list,
        filter_opts=filter_opts,
        selected_state=state,
        selected_district=district,
        selected_crop=crop_name,
        search_query=search,
        top_stats=top_stats,
        latest_update=latest_update
    )

@mandi_bp.route('/sync', methods=['POST'])
def sync_data():
    """Trigger sync with official government data.gov.in AGMARKNET API."""
    result = AgmarknetService.sync_from_datagov()
    if result.get('success'):
        flash(result.get('message'), "success")
    else:
        flash(result.get('message'), "info")
    return redirect(url_for('mandi.prices'))

@mandi_bp.route('/api/search')
def api_search():
    """API endpoint for fast client-side live filter."""
    state = request.args.get('state')
    crop = request.args.get('crop')
    prices = AgmarknetService.get_prices(state=state, crop_name=crop, limit=50)
    data = [dict(row) for row in prices]
    return jsonify({'success': True, 'prices': data})
