

from django.shortcuts import render, redirect, get_object_or_404
from .models import Polygon, Details, tools, Crop, ResourceItem
from .forms import PolygonForm, RegistrationForm
import requests
import json
import os
import numpy as np
from datetime import datetime, timedelta
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse, HttpResponse, Http404
from django.views import View
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from io import BytesIO
from PIL import Image

@login_required
def dashboard(request):
    try:
        # Get polygons without filtering by user to avoid the user field issue
        all_polygons = Polygon.objects.all()
        if not all_polygons.exists():
            # If no polygons exist, create a default context with empty data
            context = {
                "weather": [],
                "news": [],
                "error": "No farm polygons found. Please add a farm polygon first."
            }
            return render(request, 'myapp/dashboard.html', context)
            
        polygon = all_polygons.first()
        polygon_id = polygon.polygon_id
        
        # Get API key from details
        try:
            details = Details.objects.get(polygon=polygon)
            api = details.api_key
        except Details.DoesNotExist:
            api = "b4dfb6aa45d5601e695f381d85217b11"  # Fallback API key
        
        # Fetch polygon data
        try:
            result = requests.get(f"https://api.agromonitoring.com/agro/1.0/polygons/{polygon_id}?appid={api}")
            result.raise_for_status()  # Raise exception for 4XX/5XX responses
            polygon_data = result.json()
            
            # Fetch weather data
            weather_url = f"https://api.agromonitoring.com/agro/1.0/weather?lat={polygon_data['center'][1]}&lon={polygon_data['center'][0]}&appid={api}"
            weather_response = requests.get(weather_url)
            weather_response.raise_for_status()
            weather_data = weather_response.json()
        except requests.exceptions.RequestException as e:
            # Handle API request errors
            print(f"Error fetching data: {e}")
            weather_data = {}
            polygon_data = {}
        
        # Fetch news data
        try:
            news_api_key = 'ffe32e11bcce44b8b1877ca0af6cbf35'
            current_date = datetime.now().strftime("%Y-%m-%d")
            news_url = f"https://newsapi.org/v2/everything?q=agriculture+farming&from={current_date}&sortBy=publishedAt&apiKey={news_api_key}"
            news_response = requests.get(news_url)
            news_response.raise_for_status()
            news_data = news_response.json().get('articles', [])[:3]  # Get top 3 news articles
        except requests.exceptions.RequestException as e:
            print(f"Error fetching news: {e}")
            news_data = []

        context = {
            "weather": weather_data,
            "polygon": polygon_data,
            "news": news_data
        }
        return render(request, 'myapp/dashboard.html', context)
    except Exception as e:
        # Catch-all for any other errors
        print(f"Dashboard error: {e}")
        context = {
            "weather": [],
            "news": [],
            "error": "An error occurred while loading dashboard data."
        }
        return render(request, 'myapp/dashboard.html', context)


@login_required
def services(request):
    return render(request, 'myapp/services.html')
@login_required
def Tool(request):
    """Agricultural tools page with Amazon product links."""
    tool_categories = [
        {
            "name": "Hand Tools & Implements",
            "icon": "🔧",
            "items": [
                {"title": "Gardening Hand Trowel Set (3-piece)", "img": "https://placehold.co/500x500/10b981/ffffff?text=Gardening%20Hand%20Trowel%20Set", "price": "₹349", "link": "https://www.amazon.in/s?k=gardening+hand+trowel+set", "brand": "Ugaoo"},
                {"title": "Garden Cultivator Hand Fork", "img": "https://placehold.co/500x500/10b981/ffffff?text=Garden%20Cultivator%20Hand%20Fork", "price": "₹249", "link": "https://www.amazon.in/s?k=garden+hand+cultivator+fork", "brand": "Amazon"},
                {"title": "Khurpi Weeding Tool Steel", "img": "https://placehold.co/500x500/10b981/ffffff?text=Khurpi%20Weeding%20Tool%20Steel", "price": "₹199", "link": "https://www.amazon.in/s?k=khurpi+weeding+tool", "brand": "Ketsy"},
                {"title": "Garden Spade Shovel with D-Handle", "img": "https://placehold.co/500x500/10b981/ffffff?text=Garden%20Spade%20Shovel%20with", "price": "₹799", "link": "https://www.amazon.in/s?k=garden+spade+shovel", "brand": "Skyla"},
                {"title": "Garden Hoe for Weeding", "img": "https://placehold.co/500x500/10b981/ffffff?text=Garden%20Hoe%20for%20Weeding", "price": "₹549", "link": "https://www.amazon.in/s?k=garden+hoe+weeding", "brand": "Ketsy"},
            ]
        },
        {
            "name": "Irrigation & Watering",
            "icon": "💧",
            "items": [
                {"title": "Drip Irrigation Kit (20 Plants)", "img": "https://placehold.co/500x500/10b981/ffffff?text=Drip%20Irrigation%20Kit%20%2820", "price": "₹699", "link": "https://www.amazon.in/s?k=drip+irrigation+kit", "brand": "Zeal"},
                {"title": "Garden Water Sprinkler 360° Rotating", "img": "https://placehold.co/500x500/10b981/ffffff?text=Garden%20Water%20Sprinkler%20360%C2%B0", "price": "₹399", "link": "https://www.amazon.in/s?k=garden+water+sprinkler+rotating", "brand": "Kraft Seeds"},
                {"title": "Drip Tape Roll 50m with Emitters", "img": "https://placehold.co/500x500/10b981/ffffff?text=Drip%20Tape%20Roll%2050m", "price": "₹549", "link": "https://www.amazon.in/s?k=drip+tape+irrigation", "brand": "Suraj"},
                {"title": "Garden Hose Pipe 30m Heavy Duty", "img": "https://placehold.co/500x500/10b981/ffffff?text=Garden%20Hose%20Pipe%2030m", "price": "₹1,299", "link": "https://www.amazon.in/s?k=garden+hose+pipe+30m", "brand": "Visko"},
                {"title": "Manual Knapsack Sprayer 16L", "img": "https://placehold.co/500x500/10b981/ffffff?text=Manual%20Knapsack%20Sprayer%2016L", "price": "₹1,499", "link": "https://www.amazon.in/s?k=knapsack+sprayer+16+litre", "brand": "Neptune"},
            ]
        },
        {
            "name": "Soil Testing & Meters",
            "icon": "🧪",
            "items": [
                {"title": "3-in-1 Soil pH/Moisture/Light Meter", "img": "https://placehold.co/500x500/10b981/ffffff?text=3-in-1%20Soil%20pH/Moisture/Light%20Meter", "price": "₹599", "link": "https://www.amazon.in/s?k=soil+ph+moisture+light+meter", "brand": "Dr.meter"},
                {"title": "Digital Soil Moisture Meter Professional", "img": "https://placehold.co/500x500/10b981/ffffff?text=Digital%20Soil%20Moisture%20Meter", "price": "₹799", "link": "https://www.amazon.in/s?k=digital+soil+moisture+meter", "brand": "Phtronics"},
                {"title": "NPK Soil Test Kit (50 Tests)", "img": "https://placehold.co/500x500/10b981/ffffff?text=NPK%20Soil%20Test%20Kit", "price": "₹999", "link": "https://www.amazon.in/s?k=npk+soil+test+kit", "brand": "Agri"},
                {"title": "Digital pH Meter Waterproof", "img": "https://placehold.co/500x500/10b981/ffffff?text=Digital%20pH%20Meter%20Waterproof", "price": "₹1,299", "link": "https://www.amazon.in/s?k=digital+ph+meter+soil+water", "brand": "HM Digital"},
                {"title": "Soil Test Kit Basic (Organic India)", "img": "https://placehold.co/500x500/10b981/ffffff?text=Soil%20Test%20Kit%20Basic", "price": "₹449", "link": "https://www.amazon.in/s?k=soil+test+kit+india", "brand": "Organic India"},
            ]
        },
        {
            "name": "Power Tools & Equipment",
            "icon": "⚡",
            "items": [
                {"title": "Electric Cultivator Tiller 900W", "img": "https://placehold.co/500x500/10b981/ffffff?text=Electric%20Cultivator%20Tiller%20900W", "price": "₹4,999", "link": "https://www.amazon.in/s?k=electric+cultivator+tiller", "brand": "Kisankraft"},
                {"title": "Portable Electric Sprayer 16L", "img": "https://placehold.co/500x500/10b981/ffffff?text=Portable%20Electric%20Sprayer%2016L", "price": "₹3,499", "link": "https://www.amazon.in/s?k=electric+sprayer+16+litre+farm", "brand": "Neptune"},
                {"title": "Battery Grass Trimmer 20V", "img": "https://placehold.co/500x500/10b981/ffffff?text=Battery%20Grass%20Trimmer%2020V", "price": "₹2,499", "link": "https://www.amazon.in/s?k=cordless+grass+trimmer+20v", "brand": "BLACK+DECKER"},
                {"title": "Chainsaw Electric 2000W", "img": "https://placehold.co/500x500/10b981/ffffff?text=Chainsaw%20Electric%202000W", "price": "₹3,999", "link": "https://www.amazon.in/s?k=electric+chainsaw+2000w", "brand": "Bosch"},
                {"title": "Electric Seed Drill Planter", "img": "https://placehold.co/500x500/10b981/ffffff?text=Electric%20Seed%20Drill%20Planter", "price": "₹1,899", "link": "https://www.amazon.in/s?k=seed+drill+planter+electric", "brand": "Agri"},
            ]
        },
        {
            "name": "Plant Protection",
            "icon": "🛡️",
            "items": [
                {"title": "Insect Pest Catching Sticky Traps (20 pcs)", "img": "https://placehold.co/500x500/10b981/ffffff?text=Insect%20Pest%20Catching%20Sticky", "price": "₹199", "link": "https://www.amazon.in/s?k=sticky+insect+trap+yellow+farm", "brand": "Kraft Seeds"},
                {"title": "Bird Repeller Net 4m x 5m", "img": "https://placehold.co/500x500/10b981/ffffff?text=Bird%20Repeller%20Net%204m", "price": "₹349", "link": "https://www.amazon.in/s?k=bird+net+farm+garden", "brand": "Agri"},
                {"title": "Garden Cover Mesh Shade Net 50%", "img": "https://placehold.co/500x500/10b981/ffffff?text=Garden%20Cover%20Mesh%20Shade", "price": "₹499", "link": "https://www.amazon.in/s?k=shade+net+50+percent", "brand": "Singhal"},
                {"title": "Bio Pesticide Neem Oil 100ml", "img": "https://placehold.co/500x500/10b981/ffffff?text=Bio%20Pesticide%20Neem%20Oil", "price": "₹249", "link": "https://www.amazon.in/s?k=neem+oil+farm+bio+pesticide", "brand": "Organic India"},
                {"title": "Electric Rat Trap", "img": "https://placehold.co/500x500/10b981/ffffff?text=Electric%20Rat%20Trap", "price": "₹1,299", "link": "https://www.amazon.in/s?k=electric+rat+trap", "brand": "Victor"},
            ]
        },
    ]
    return render(request, 'myapp/tools.html', {'tool_categories': tool_categories})

def about(request):
    return render(request, 'myapp/about.html')
@login_required
def resources(request):
    return render(request, 'myapp/resources.html')
@login_required
def resources_view(request):
    """Resources page with comprehensive Amazon product categories."""
    categories = [
        {
            "name": "Seeds & Planting Material",
            "icon": "🌱",
            "items": [
                {"title": "Hybrid Tomato Seeds (Arka Rakshak)", "img": "https://placehold.co/500x500/10b981/ffffff?text=Hybrid%20Tomato%20Seeds%20%28Arka", "link": "https://www.amazon.in/s?k=hybrid+tomato+seeds+arka+rakshak", "price_range": "₹45-200"},
                {"title": "Cucumber Seeds F1 Hybrid (50 seeds)", "img": "https://placehold.co/500x500/10b981/ffffff?text=Cucumber%20Seeds%20F1%20Hybrid", "link": "https://www.amazon.in/s?k=cucumber+f1+hybrid+seeds", "price_range": "₹55-150"},
                {"title": "Marigold Flower Seeds Mix (500 seeds)", "img": "https://placehold.co/500x500/10b981/ffffff?text=Marigold%20Flower%20Seeds%20Mix", "link": "https://www.amazon.in/s?k=marigold+seeds+500", "price_range": "₹99-299"},
                {"title": "Green Chilli Seeds Hybrid", "img": "https://placehold.co/500x500/10b981/ffffff?text=Green%20Chilli%20Seeds%20Hybrid", "link": "https://www.amazon.in/s?k=green+chilli+seeds+hybrid", "price_range": "₹49-199"},
                {"title": "Spinach Seeds Palak (250g)", "img": "https://placehold.co/500x500/10b981/ffffff?text=Spinach%20Seeds%20Palak%20%28250g%29", "link": "https://www.amazon.in/s?k=spinach+palak+seeds+250g", "price_range": "₹49-149"},
                {"title": "Bitter Gourd Karela Seeds Hybrid", "img": "https://placehold.co/500x500/10b981/ffffff?text=Bitter%20Gourd%20Karela%20Seeds", "link": "https://www.amazon.in/s?k=karela+bitter+gourd+seeds", "price_range": "₹45-180"},
                {"title": "Watermelon Seeds (Black Diamond)", "img": "https://placehold.co/500x500/10b981/ffffff?text=Watermelon%20Seeds%20%28Black%20Diamond%29", "link": "https://www.amazon.in/s?k=watermelon+seeds+hybrid", "price_range": "₹99-399"},
                {"title": "Brinjal/Eggplant Seeds Hybrid", "img": "https://placehold.co/500x500/10b981/ffffff?text=Brinjal/Eggplant%20Seeds%20Hybrid", "link": "https://www.amazon.in/s?k=brinjal+eggplant+seeds+hybrid", "price_range": "₹45-150"},
            ]
        },
        {
            "name": "Fertilizers & Nutrients",
            "icon": "💊",
            "items": [
                {"title": "Organic Vermicompost (5kg bag)", "img": "https://placehold.co/500x500/10b981/ffffff?text=Organic%20Vermicompost%20%285kg%20bag%29", "link": "https://www.amazon.in/s?k=vermicompost+5kg+organic", "price_range": "₹199-499"},
                {"title": "NPK 19-19-19 Water Soluble (1kg)", "img": "https://placehold.co/500x500/10b981/ffffff?text=NPK%2019-19-19%20Water%20Soluble", "link": "https://www.amazon.in/s?k=npk+19+19+19+water+soluble+fertilizer", "price_range": "₹299-699"},
                {"title": "Urea Fertilizer 1kg", "img": "https://placehold.co/500x500/10b981/ffffff?text=Urea%20Fertilizer%201kg", "link": "https://www.amazon.in/s?k=urea+fertilizer+1kg", "price_range": "₹99-249"},
                {"title": "Neem Cake Organic Fertilizer 2kg", "img": "https://placehold.co/500x500/10b981/ffffff?text=Neem%20Cake%20Organic%20Fertilizer", "link": "https://www.amazon.in/s?k=neem+cake+fertilizer+2kg", "price_range": "₹149-399"},
                {"title": "Potassium Humate Granules 1kg", "img": "https://placehold.co/500x500/10b981/ffffff?text=Potassium%20Humate%20Granules%201kg", "link": "https://www.amazon.in/s?k=potassium+humate+granules", "price_range": "₹399-799"},
                {"title": "Seaweed Extract Fertilizer 250ml", "img": "https://placehold.co/500x500/10b981/ffffff?text=Seaweed%20Extract%20Fertilizer%20250ml", "link": "https://www.amazon.in/s?k=seaweed+extract+fertilizer", "price_range": "₹349-799"},
                {"title": "Bone Meal Fertilizer 1kg", "img": "https://placehold.co/500x500/10b981/ffffff?text=Bone%20Meal%20Fertilizer%201kg", "link": "https://www.amazon.in/s?k=bone+meal+fertilizer+1kg", "price_range": "₹199-499"},
            ]
        },
        {
            "name": "Pesticides & Crop Protection",
            "icon": "🛡️",
            "items": [
                {"title": "Neem Oil Cold Pressed 500ml (Bio)", "img": "https://placehold.co/500x500/10b981/ffffff?text=Neem%20Oil%20Cold%20Pressed", "link": "https://www.amazon.in/s?k=neem+oil+cold+pressed+500ml", "price_range": "₹299-699"},
                {"title": "Copper Oxychloride Fungicide 500g", "img": "https://placehold.co/500x500/10b981/ffffff?text=Copper%20Oxychloride%20Fungicide%20500g", "link": "https://www.amazon.in/s?k=copper+oxychloride+fungicide", "price_range": "₹249-599"},
                {"title": "Mancozeb Fungicide 500g", "img": "https://placehold.co/500x500/10b981/ffffff?text=Mancozeb%20Fungicide%20500g", "link": "https://www.amazon.in/s?k=mancozeb+fungicide+500g", "price_range": "₹199-499"},
                {"title": "Yellow Sticky Trap Insect Board (20pcs)", "img": "https://placehold.co/500x500/10b981/ffffff?text=Yellow%20Sticky%20Trap%20Insect", "link": "https://www.amazon.in/s?k=yellow+sticky+insect+trap+agriculture", "price_range": "₹149-399"},
                {"title": "Bio Pesticide Trichoderma 1kg", "img": "https://placehold.co/500x500/10b981/ffffff?text=Bio%20Pesticide%20Trichoderma%201kg", "link": "https://www.amazon.in/s?k=trichoderma+bio+pesticide+1kg", "price_range": "₹299-599"},
                {"title": "Imidacloprid Insecticide 100ml", "img": "https://placehold.co/500x500/10b981/ffffff?text=Imidacloprid%20Insecticide%20100ml", "link": "https://www.amazon.in/s?k=imidacloprid+insecticide", "price_range": "₹249-549"},
            ]
        },
        {
            "name": "Irrigation Equipment",
            "icon": "💧",
            "items": [
                {"title": "Complete Drip Irrigation Kit (100 Plants)", "img": "https://placehold.co/500x500/10b981/ffffff?text=Complete%20Drip%20Irrigation%20Kit", "link": "https://www.amazon.in/s?k=drip+irrigation+kit+100+plants", "price_range": "₹1,999-4,999"},
                {"title": "Submersible Water Pump 1HP", "img": "https://placehold.co/500x500/10b981/ffffff?text=Submersible%20Water%20Pump%201HP", "link": "https://www.amazon.in/s?k=submersible+water+pump+1hp+agriculture", "price_range": "₹3,499-7,999"},
                {"title": "Micro Sprinkler Irrigation System", "img": "https://placehold.co/500x500/10b981/ffffff?text=Micro%20Sprinkler%20Irrigation%20System", "link": "https://www.amazon.in/s?k=micro+sprinkler+irrigation+system", "price_range": "₹999-3,499"},
                {"title": "Rain Gun Sprinkler 1 Inch", "img": "https://placehold.co/500x500/10b981/ffffff?text=Rain%20Gun%20Sprinkler%201", "link": "https://www.amazon.in/s?k=rain+gun+sprinkler+1+inch+agriculture", "price_range": "₹1,499-3,999"},
                {"title": "PE Poly Tube 16mm Roll (100m)", "img": "https://placehold.co/500x500/10b981/ffffff?text=PE%20Poly%20Tube%2016mm", "link": "https://www.amazon.in/s?k=pe+poly+tube+16mm+drip", "price_range": "₹799-1,499"},
            ]
        },
        {
            "name": "Greenhouse & Protective Covers",
            "icon": "🏠",
            "items": [
                {"title": "UV Stabilized Polyhouse Film 200 Micron", "img": "https://placehold.co/500x500/10b981/ffffff?text=UV%20Stabilized%20Polyhouse%20Film", "link": "https://www.amazon.in/s?k=polyhouse+film+uv+stabilized+greenhouse", "price_range": "₹2,999-8,999"},
                {"title": "50% Shade Net Green 3x5 Meter", "img": "https://placehold.co/500x500/10b981/ffffff?text=50%25%20Shade%20Net%20Green", "link": "https://www.amazon.in/s?k=shade+net+50+percent+agriculture", "price_range": "₹399-999"},
                {"title": "Anti-hail Net for Farm Protection", "img": "https://placehold.co/500x500/10b981/ffffff?text=Anti-hail%20Net%20for%20Farm", "link": "https://www.amazon.in/s?k=anti+hail+net+farm", "price_range": "₹999-3,999"},
                {"title": "Insect-proof Net 40 Mesh Roll", "img": "https://placehold.co/500x500/10b981/ffffff?text=Insect-proof%20Net%2040%20Mesh", "link": "https://www.amazon.in/s?k=insect+proof+net+40+mesh", "price_range": "₹799-2,499"},
                {"title": "Mulching Film Black 1.2m x 100m", "img": "https://placehold.co/500x500/10b981/ffffff?text=Mulching%20Film%20Black%201.2m", "link": "https://www.amazon.in/s?k=mulching+film+black+1.2m+agriculture", "price_range": "₹1,299-3,499"},
            ]
        },
        {
            "name": "Books & Learning Resources",
            "icon": "📚",
            "items": [
                {"title": "Modern Vegetable Farming (Hindi)", "img": "https://placehold.co/500x500/10b981/ffffff?text=Modern%20Vegetable%20Farming%20%28Hindi%29", "link": "https://www.amazon.in/s?k=modern+vegetable+farming+book+hindi", "price_range": "₹199-499"},
                {"title": "Organic Farming Complete Guide", "img": "https://placehold.co/500x500/10b981/ffffff?text=Organic%20Farming%20Complete%20Guide", "link": "https://www.amazon.in/s?k=organic+farming+complete+guide+book", "price_range": "₹299-699"},
                {"title": "Soil Science and Management Book", "img": "https://placehold.co/500x500/10b981/ffffff?text=Soil%20Science%20and%20Management", "link": "https://www.amazon.in/s?k=soil+science+management+agriculture+book", "price_range": "₹399-899"},
                {"title": "Drip Irrigation Design Manual", "img": "https://placehold.co/500x500/10b981/ffffff?text=Drip%20Irrigation%20Design%20Manual", "link": "https://www.amazon.in/s?k=drip+irrigation+design+manual+book", "price_range": "₹249-549"},
                {"title": "Pest Management in Agriculture", "img": "https://placehold.co/500x500/10b981/ffffff?text=Pest%20Management%20in%20Agriculture", "link": "https://www.amazon.in/s?k=pest+management+agriculture+book", "price_range": "₹349-799"},
            ]
        },
        {
            "name": "Grow Bags & Containers",
            "icon": "🪴",
            "items": [
                {"title": "HDPE Grow Bag 15L (Pack of 10)", "img": "https://placehold.co/500x500/10b981/ffffff?text=HDPE%20Grow%20Bag%2015L", "link": "https://www.amazon.in/s?k=hdpe+grow+bag+15+litre+pack+10", "price_range": "₹299-699"},
                {"title": "Fabric Grow Bag 20L (Pack of 5)", "img": "https://placehold.co/500x500/10b981/ffffff?text=Fabric%20Grow%20Bag%2020L", "link": "https://www.amazon.in/s?k=fabric+grow+bag+20+litre", "price_range": "₹249-599"},
                {"title": "Terracotta Pots Large 14 inch (Pack of 3)", "img": "https://placehold.co/500x500/10b981/ffffff?text=Terracotta%20Pots%20Large%2014", "link": "https://www.amazon.in/s?k=terracotta+pot+14+inch+pack+3", "price_range": "₹399-999"},
                {"title": "Seedling Tray 98 Holes (Pack of 5)", "img": "https://placehold.co/500x500/10b981/ffffff?text=Seedling%20Tray%2098%20Holes", "link": "https://www.amazon.in/s?k=seedling+tray+98+holes", "price_range": "₹149-399"},
                {"title": "Coir Pith Block 5kg (Expands to 75L)", "img": "https://placehold.co/500x500/10b981/ffffff?text=Coir%20Pith%20Block%205kg", "link": "https://www.amazon.in/s?k=coir+pith+block+5kg", "price_range": "₹249-599"},
            ]
        },
        {
            "name": "Safety & Protective Gear",
            "icon": "🦺",
            "items": [
                {"title": "Chemical Resistant Gloves (Pair)", "img": "https://placehold.co/500x500/10b981/ffffff?text=Chemical%20Resistant%20Gloves%20%28Pair%29", "link": "https://www.amazon.in/s?k=chemical+resistant+gloves+farming", "price_range": "₹149-399"},
                {"title": "N95 Dust Mask Respirator (10 pcs)", "img": "https://placehold.co/500x500/10b981/ffffff?text=N95%20Dust%20Mask%20Respirator", "link": "https://www.amazon.in/s?k=n95+dust+mask+farming+10+pack", "price_range": "₹199-499"},
                {"title": "Farm Work Rain Boot/Gumboot", "img": "https://placehold.co/500x500/10b981/ffffff?text=Farm%20Work%20Rain%20Boot/Gumboot", "link": "https://www.amazon.in/s?k=gumboot+rain+boot+farming", "price_range": "₹399-999"},
                {"title": "Protective Safety Goggles Farm", "img": "https://placehold.co/500x500/10b981/ffffff?text=Protective%20Safety%20Goggles%20Farm", "link": "https://www.amazon.in/s?k=protective+safety+goggles+farm", "price_range": "₹199-499"},
                {"title": "Apron Chemical Resistant PVC", "img": "https://placehold.co/500x500/10b981/ffffff?text=Apron%20Chemical%20Resistant%20PVC", "link": "https://www.amazon.in/s?k=pvc+apron+chemical+resistant", "price_range": "₹299-699"},
            ]
        },
    ]
    search_query = request.GET.get('q', '').strip()
    selected_category = request.GET.get('category', '').strip()

    if search_query:
        categories = [
            {
                **cat, 
                'items': [item for item in cat['items'] if search_query.lower() in item['title'].lower()]
            } 
            for cat in categories
        ]
        categories = [cat for cat in categories if cat['items']]

    if selected_category:
        categories = [cat for cat in categories if cat['name'] == selected_category]

    all_category_names = [
        "Seeds & Planting Material", "Fertilizers & Nutrients", "Pesticides & Crop Protection",
        "Irrigation Equipment", "Greenhouse & Protective Covers", "Books & Learning Resources",
        "Grow Bags & Containers", "Safety & Protective Gear",
    ]
    return render(request, 'myapp/resources.html', {
        'categories': categories, 'search_query': search_query, 
        'selected_category': selected_category, 'all_category_names': all_category_names,
    })
@login_required
def market(request):
    crops = Crop.objects.prefetch_related('historical_prices').all().order_by('name')
    return render(request, 'myapp/market.html', {'crops': crops})
@login_required
def trade(request):
    return render(request, 'myapp/trade.html')

def login_page(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    
    return render(request, 'myapp/login.html', {'form': form})
def handlelogout(request):
    logout(request)
    return redirect('/login')
def logout_view(request):
    logout(request)
    return redirect('login')
def privacy(request):
    return render(request,'myapp/privacy.html')

def TandC(request):
    return render(request,'myapp/TandC.html')

def FAQs(request):
    return render(request,'myapp/FAQs.html')

def add_polygon(request):
    if request.method == 'POST':
        form = PolygonForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('polygon_list')
    else:
        form = PolygonForm()
    return render(request, 'myapp/add_polygon.html', {'form': form})

def polygon_list(request):
    polygons = Polygon.objects.all()
    return render(request, 'myapp/polygon_list.html', {'polygons': polygons})
@login_required
def news(request):
    # Get filter parameters from request or use defaults
    category = request.GET.get('category', 'agriculture')
    sort_by = request.GET.get('sort_by', 'publishedAt')
    page = int(request.GET.get('page', 1))
    items_per_page = 9
    
    # Define agriculture-related keywords for better filtering
    agriculture_keywords = [
        'agriculture', 'farming', 'crops', 'harvest', 'soil', 'irrigation',
        'sustainable farming', 'organic farming', 'precision agriculture',
        'farm technology', 'agritech', 'agricultural innovation'
    ]
    
    # Randomly select 3 keywords to diversify results while keeping them agriculture-focused
    import random
    selected_keywords = random.sample(agriculture_keywords, 3)
    query_string = ' OR '.join(selected_keywords)
    
    if category != 'agriculture':
        query_string = f"{query_string} AND {category}"
    
    # API key
    api_key = 'ffe32e11bcce44b8b1877ca0af6cbf35'
    
    # Construct URL with dynamic parameters
    url = f"https://newsapi.org/v2/everything?q={query_string}&sortBy={sort_by}&pageSize={items_per_page}&page={page}&apiKey={api_key}"
    
    try:
        # Fetch news data
        response = requests.get(url)
        news_data = response.json()
        
        if response.status_code == 200 and news_data.get('status') == 'ok':
            articles = news_data.get('articles', [])
            total_results = news_data.get('totalResults', 0)
            
            # Process articles
            # Create lists for the template - only use title, desc, img to match template expectations
            title = []
            desc = []
            img = []
            
            for article in articles:
                # Only include articles with all required fields
                if all(article.get(field) for field in ['title', 'description', 'urlToImage']):
                    title.append(article['title'])
                    desc.append(article['description'])
                    img.append(article['urlToImage'])
            
            # Calculate pagination info
            total_pages = min(10, (total_results + items_per_page - 1) // items_per_page)  # Limit to 10 pages max
            has_next = page < total_pages
            has_prev = page > 1
            
            # Create context with all necessary data - only zip the 3 values expected by template
            mylist = zip(title, desc, img)
            context = {
                'mylist': mylist,
                'current_page': page,
                'total_pages': total_pages,
                'has_next': has_next,
                'has_prev': has_prev,
                'next_page': page + 1 if has_next else page,
                'prev_page': page - 1 if has_prev else page,
                'category': category,
                'sort_by': sort_by,
                'categories': ['agriculture', 'technology', 'sustainability', 'climate', 'policy', 'market'],
                'sort_options': [('publishedAt', 'Latest'), ('relevancy', 'Relevant'), ('popularity', 'Popular')]
            }
        else:
            # Handle API error
            context = {
                'error': f"Error fetching news: {news_data.get('message', 'Unknown error')}",
                'mylist': []
            }
    except Exception as e:
        # Handle request exception
        context = {
            'error': f"Error connecting to news service: {str(e)}",
            'mylist': []
        }
    
    return render(request, 'myapp/news.html', context)

def get_agro_data(request, polygon_id):
    api_key = 'b4dfb6aa45d5601e695f381d85217b11'
    url = f'https://api.agromonitoring.com/data?api_key={api_key}&polygon_id={polygon_id}'
    response = requests.get(url)
    data = response.json() if response.status_code == 200 else None
    return render(request, 'myapp/agro_data.html', {'data': data})

def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Add custom field handling here if needed
            # For example, if you have a Profile model:
            # profile = user.profile
            # profile.polygon_id = form.cleaned_data.get('polygon_id')
            # profile.save()
            
            login(request, user)
                
            return redirect('dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = RegistrationForm()
    
    return render(request, 'myapp/register.html', {'form': form})

def fetch_weather_data(polygon_id):
    api_key = 'b4dfb6aa45d5601e695f381d85217b11'
    url = f'https://api.agromonitoring.com/data?api_key={api_key}&polygon_id={polygon_id}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def weather_dashboard(request):
    # Assuming you want to display data for the first polygon
    polygon = Polygon.objects.first()
    data = fetch_weather_data(polygon.polygon_id) if polygon else None
    return render(request, 'myapp/weather_dashboard.html', {'data': data})

def main_dashboard(request):
    # Assuming you want to display data for the first polygon
    polygon = Polygon.objects.first()
    data = fetch_weather_data(polygon.polygon_id) if polygon else None
    return render(request, 'myapp/main_dashboard.html', {'data': data})
@login_required
def details(request, polygon_identifier=None, polygon_id=None):
    """Display details for a given polygon by ID or name."""
    # If polygon_identifier not provided but polygon_id is (old URL param name), treat it the same
    if polygon_identifier is None and polygon_id is not None:
        polygon_identifier = polygon_id

    # Fetch the Polygon object either by its polygon_id or by its name
    polygon_obj = None
    if polygon_identifier:
        try:
            polygon_obj = Polygon.objects.get(polygon_id=polygon_identifier)
        except Polygon.DoesNotExist:
            try:
                polygon_obj = Polygon.objects.get(name=polygon_identifier)
            except Polygon.DoesNotExist:
                polygon_obj = None

    if polygon_obj is None:
        # Show 404 if not found
        raise Http404("Polygon not found")

    # At this point we definitely have a polygon object
    polygon_id_value = polygon_obj.polygon_id

    # Get user input for start and end dates
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Convert dates to Unix timestamp if provided
    if end_date:
        end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
        end_datetime = timezone.make_aware(end_datetime, timezone.get_current_timezone())  # Make it timezone-aware
        end_timestamp = int(end_datetime.timestamp())
    else:
        # Default end timestamp: current time
        end_timestamp = int(timezone.now().timestamp())

    if start_date:
        start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
        start_datetime = timezone.make_aware(start_datetime, timezone.get_current_timezone())  # Make it timezone-aware
        start_timestamp = int(start_datetime.timestamp())
    else:
        # Default start timestamp: 30 days ago
        start_timestamp = int((timezone.now() - timedelta(days=30)).timestamp())

    # Determine API key for this polygon
    try:
        details_obj = Details.objects.get(polygon=polygon_obj)
        api_key = details_obj.api_key
    except Details.DoesNotExist:
        api_key = "b4dfb6aa45d5601e695f381d85217b11"  # Fallback key

    # Fetch data from the API
    result = requests.get(f"https://api.agromonitoring.com/agro/1.0/polygons/{polygon_id_value}?appid={api_key}")
    ndvi = requests.get(f"https://api.agromonitoring.com/agro/1.0/ndvi/history?start={start_timestamp}&end={end_timestamp}&polyid={polygon_id_value}&appid={api_key}")
    # Need lat lon from polygon result JSON
    result_json = result.json()
    lat = result_json.get('center', [0,0])[1]
    lon = result_json.get('center', [0,0])[0]
    weather = requests.get(f"https://api.agromonitoring.com/agro/1.0/weather/forecast?lat={lat}&lon={lon}&appid={api_key}")
    soil = requests.get(f"https://api.agromonitoring.com/agro/1.0/soil?polyid={polygon_id_value}&appid={api_key}")
    uv_index = requests.get(f"https://api.agromonitoring.com/agro/1.0/uvi?polyid={polygon_id_value}&appid={api_key}")

    # Process UV index data
    uv_index_data = uv_index.json()
    if isinstance(uv_index_data, dict) and uv_index_data.get('dt') is not None:
        uv_index_value = uv_index_data.get('uvi')
        uv_index_date = datetime.utcfromtimestamp(uv_index_data.get('dt')).strftime('%Y-%m-%d %H:%M:%S')
    else:
        # Handle cases where the API does not return data (e.g., outside valid range for UVI)
        uv_index_value = None
        uv_index_date = None

    # Process vegetation index data
    ndvi_data = ndvi.json()
    index_type = request.GET.get('index_type', 'NDVI')
    available_indices = ['NDVI', 'EVI', 'SAVI']
    
    # Prepare vegetation index data for the chart
    veg_index_data = {
        'dates': [],
        'min_values': [],
        'mean_values': [],
        'max_values': [],
        'health_status': 'Good',
        'health_trend': 'Stable'
    }
    
    # Process NDVI data from API
    if ndvi_data and isinstance(ndvi_data, list) and len(ndvi_data) > 0:
        # Sort by date (ascending)
        ndvi_data.sort(key=lambda x: x.get('dt', 0))
        
        # Extract dates and values
        for entry in ndvi_data:
            date_str = datetime.utcfromtimestamp(entry.get('dt', 0)).strftime('%Y-%m-%d')
            veg_index_data['dates'].append(date_str)
            veg_index_data['min_values'].append(entry.get('data', {}).get('min', 0))
            veg_index_data['mean_values'].append(entry.get('data', {}).get('mean', 0))
            veg_index_data['max_values'].append(entry.get('data', {}).get('max', 0))
        
        # Determine health status based on latest mean value
        if veg_index_data['mean_values']:
            latest_value = veg_index_data['mean_values'][-1]
            if latest_value > 0.6:
                veg_index_data['health_status'] = 'Excellent'
            elif latest_value > 0.4:
                veg_index_data['health_status'] = 'Good'
            elif latest_value > 0.2:
                veg_index_data['health_status'] = 'Fair'
            else:
                veg_index_data['health_status'] = 'Poor'
        
        # Determine trend based on last few values
        if len(veg_index_data['mean_values']) > 1:
            last_value = veg_index_data['mean_values'][-1]
            prev_value = veg_index_data['mean_values'][-2]
            diff = last_value - prev_value
            
            if diff > 0.05:
                veg_index_data['health_trend'] = 'Improving'
            elif diff < -0.05:
                veg_index_data['health_trend'] = 'Declining'
            else:
                veg_index_data['health_trend'] = 'Stable'

    return render(request, "myapp/details.html", {
        "api_data_json": result.json(),
        "ndvi_data_json": json.dumps(ndvi_data),
        "start_date": start_date,
        "end_date": end_date,
        "polygon_id": polygon_id_value,
        "weather": json.dumps(weather.json()),
        "soil": json.dumps(soil.json()),
        "uv_index_value": uv_index_value,
        "uv_index_date": uv_index_date,
        "veg_index_data": json.dumps(veg_index_data),
        "index_type": index_type,
        "available_indices": json.dumps(available_indices),
        "polygons": Polygon.objects.all(),
     })
    
    




# Import AI model utilities
try:
    from keras.models import load_model
    from keras.preprocessing.image import img_to_array, load_img
    import numpy as np
    KERAS_AVAILABLE = True
except ImportError:
    KERAS_AVAILABLE = False

# Define model path for the new plant disease recognition model
MODEL_PATH = 'C:\\Users\\Asus\\OneDrive\\Desktop\\gc\\AgroBrain\\model\\plant_disease_recog_model_pwp.keras'

# Initialize model variable
model = None

# Try to load the trained model, but handle the case when it's not available
try:
    if KERAS_AVAILABLE:
        model = load_model(MODEL_PATH)
        MODEL_AVAILABLE = True
        print("Successfully loaded plant disease recognition model")
    else:
        MODEL_AVAILABLE = False
        print("Keras is not available; plant disease model disabled")
except Exception as e:
    print(f"Error loading model: {str(e)}")
    MODEL_AVAILABLE = False

# Advanced class labels (ensure class labels match your dataset)
CLASS_LABELS = [
    "Apple_scab", "Apple_black_rot", "Apple_cedar_apple_rust", "Apple_healthy",
    "Background_without_leaves", "Blueberry_healthy", "Cherry_powdery_mildew", "Cherry_healthy",
    "Corn_gray_leaf_spot", "Corn_common_rust", "Corn_northern_leaf_blight", "Corn_healthy",
    "Grape_black_rot", "Grape_black_measles", "Grape_leaf_blight", "Grape_healthy",
    "Orange_haunglongbing", "Peach_bacterial_spot", "Peach_healthy",
    "Pepper_bacterial_spot", "Pepper_healthy", "Potato_early_blight", "Potato_healthy",
    "Potato_late_blight", "Raspberry_healthy", "Soybean_healthy", "Squash_powdery_mildew",
    "Strawberry_healthy", "Strawberry_leaf_scorch", "Tomato_bacterial_spot", "Tomato_early_blight",
    "Tomato_healthy", "Tomato_late_blight", "Tomato_leaf_mold", "Tomato_septoria_leaf_spot",
    "Tomato_spider_mites_two-spotted_spider_mite", "Tomato_target_spot", "Tomato_mosaic_virus",
    "Tomato_yellow_leaf_curl_virus",
"Tomato Leaf Mold", "Tomato Septoria Leaf Spot", "Tomato Spider Mites", 
"Tomato Target Spot", "Tomato Yellow Leaf Curl Virus", "Tomato Mosaic Virus",
"Healthy Tomato"
]

from datetime import datetime
import os

@login_required
def detect_disease(request):
    # Check if the model is available, if not, show the underdevelopment page
    if not MODEL_AVAILABLE:
        messages.warning(request, "The Plant Health Analysis feature is currently under development. Please check back later.")
        return render(request, 'myapp/underdevelopment.html')
        
    if request.method == 'POST' and request.FILES.get('plant_image'):
        image_file = request.FILES['plant_image']

        # Save uploaded image with timestamp to prevent overwriting
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename, ext = os.path.splitext(image_file.name)
        safe_filename = f"{timestamp}_{filename}{ext}"
        file_path = os.path.join(settings.MEDIA_ROOT, 'plant_images', safe_filename)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Save the file
        with open(file_path, 'wb') as f:
            for chunk in image_file.chunks():
                f.write(chunk)

        # Validate and preprocess image
        try:
            img = load_img(file_path, target_size=(160, 160))
        except Exception as e:
            messages.error(request, f"Error processing image: {str(e)}")
            return redirect('plant_health')

        try:
            # Preprocess image for model input
            img_array = img_to_array(img)
            img_array = np.expand_dims(img_array, axis=0) / 255.0  

            # Predict disease with error handling
            try:
                predictions = model.predict(img_array)
                print(f"Raw predictions: {predictions}")  # Temporary logging for debugging
                predicted_class = np.argmax(predictions[0])
                confidence = float(predictions[0][predicted_class]) * 100
            except Exception as model_error:
                messages.error(request, f"Error during model prediction: {str(model_error)}")
                return redirect('plant_health')

            # Ensure class index is within bounds
            detected_disease = CLASS_LABELS[predicted_class] if predicted_class < len(CLASS_LABELS) else "Unknown"
            plant_type = detected_disease.split(" ")[0] if " " in detected_disease else detected_disease

            # Generate appropriate recommendations based on disease
            precautions = "Regular monitoring and early intervention are recommended."
            solution = "Use appropriate fungicides or organic treatments."
            
            if "Healthy" not in detected_disease:
                if "Blight" in detected_disease:
                    solution = "Remove affected leaves and apply copper-based fungicide."
                elif "Rust" in detected_disease:
                    solution = "Apply sulfur-based fungicide and ensure good air circulation."
                elif "Spot" in detected_disease:
                    solution = "Remove infected leaves and apply appropriate fungicide."
                elif "Mold" in detected_disease:
                    solution = "Improve air circulation and reduce humidity around plants."

            # Store Report
            disease_report = {
                "PlantType": plant_type,
                "DiseaseDetected": detected_disease,
                "ConfidenceLevel": f"{confidence:.2f}%",
                "Precautions": precautions,
                "Solution": solution,
                "PlantHealth": "Healthy" if "Healthy" in detected_disease else "Affected",
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "ImageURL": f"/media/plant_images/{safe_filename}"
            }

            # Store multiple reports in session
            if "past_reports" not in request.session:
                request.session["past_reports"] = []
            
            # Limit to 10 most recent reports to prevent session bloat
            past_reports = request.session["past_reports"]
            past_reports.insert(0, disease_report)  # Insert newest first
            request.session["past_reports"] = past_reports[:10]  # Keep only 10 most recent
            request.session["disease_report"] = disease_report
            request.session.modified = True  

            # Save report to database if PlantHealthReport model is available
            try:
                from .models import PlantHealthReport
                report = PlantHealthReport(
                    image=f"plant_images/{safe_filename}",
                    plant_type=plant_type,
                    disease_detected=detected_disease,
                    confidence_level=f"{confidence:.2f}%",
                    precautions=precautions,
                    solution=solution,
                    plant_health="Healthy" if "Healthy" in detected_disease else "Affected"
                )
                report.save()
            except Exception as db_error:
                # Continue even if database save fails - we still have session data
                print(f"Error saving to database: {str(db_error)}")

            return redirect('plant_health_results')
        except Exception as e:
            # If any error occurs during prediction, show error message
            messages.error(request, f"Error during disease prediction: {str(e)}")
            return redirect('plant_health')

    # Ensure past reports are passed to the upload page
    past_reports = request.session.get("past_reports", [])

    return render(request, 'myapp/plant_health.html', {"past_reports": past_reports})

@login_required
def plant_health_results(request):
    # Check if the model is available, if not, show the underdevelopment page
    if not MODEL_AVAILABLE:
        messages.warning(request, "The Plant Health Analysis feature is currently under development. Please check back later.")
        return render(request, 'myapp/underdevelopment.html')
        
    disease_report = request.session.get('disease_report', {})
    past_reports = request.session.get('past_reports', [])  # Already in newest-first order

    if not disease_report:
        messages.error(request, "No disease report found. Please upload a plant image.")
        return redirect('plant_health')

    # Ensure session is marked as modified to save changes
    request.session.modified = True

    # Get database reports if available
    db_reports = []
    try:
        from .models import PlantHealthReport
        # Get all reports without filtering by user to avoid the user field issue
        db_reports = PlantHealthReport.objects.all().order_by('-timestamp')[:5]
    except Exception as e:
        print(f"Error retrieving database reports: {str(e)}")

    return render(request, 'myapp/plant_health_results.html', {
        "report": disease_report,
        "past_reports": past_reports,
        "db_reports": db_reports
    })
from reportlab.pdfgen import canvas
@login_required
def download_report(request):
    # Check if the model is available, if not, show the underdevelopment page
    if not MODEL_AVAILABLE:
        messages.warning(request, "The Plant Health Analysis feature is currently under development. Please check back later.")
        return render(request, 'myapp/underdevelopment.html')
        
    disease_report = request.session.get('disease_report', {})

    if not disease_report:
        messages.error(request, "No report available for download. Please analyze a plant image first.")
        return redirect('plant_health')

    # Create PDF response with timestamp in filename
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"plant_disease_report_{timestamp}.pdf"
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    # Generate PDF content
    pdf = canvas.Canvas(response)
    pdf.setTitle("Plant Disease Analysis Report")

    # Add header and logo
    y = 800
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(100, y, "AgroBrain: Plant Disease Analysis Report")
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(100, y-20, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Draw a line
    pdf.line(100, y-30, 500, y-30)
    
    # Add report content
    y -= 60
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(100, y, "Analysis Results:")
    pdf.setFont("Helvetica", 12)

    # Format the report content
    important_fields = [
        "PlantType", "DiseaseDetected", "ConfidenceLevel", 
        "PlantHealth", "Precautions", "Solution", "Timestamp"
    ]
    
    for key in important_fields:
        if key in disease_report:
            y -= 25
            # Format the key for better readability
            display_key = " ".join([word.capitalize() for word in key.split("_")])
            if key == "PlantHealth":
                health_status = disease_report[key]
                pdf.drawString(100, y, f"{display_key}: {health_status}")
                # Add color indicator
                if health_status == "Healthy":
                    pdf.setFillColorRGB(0, 0.5, 0)  # Green
                else:
                    pdf.setFillColorRGB(0.8, 0, 0)  # Red
                pdf.rect(300, y, 10, 10, fill=1)
                pdf.setFillColorRGB(0, 0, 0)  # Reset to black
            else:
                pdf.drawString(100, y, f"{display_key}: {disease_report[key]}")
    
    # Add footer
    pdf.drawString(100, 50, "This report is generated by AgroBrain's Plant Disease Recognition System.")
    pdf.drawString(100, 30, "For more information, visit www.agrobrain.com")
    
    pdf.save()
    return response





@login_required
def delete_report(request, timestamp=None):
    # Check if the model is available, if not, show the underdevelopment page
    if not MODEL_AVAILABLE:
        messages.warning(request, "The Plant Health Analysis feature is currently under development. Please check back later.")
        return render(request, 'myapp/underdevelopment.html')
        
    if request.method == "POST" or timestamp:
        # Get timestamp from URL parameter if not in POST data
        if not timestamp:
            timestamp = request.POST.get("timestamp")

        if not timestamp:
            messages.error(request, "No timestamp provided for report deletion.")
            return redirect("plant_health_results")

        # Get past reports from session
        if "past_reports" in request.session:
            past_reports = request.session["past_reports"]

            # Filter out the report with the matching timestamp
            updated_reports = [r for r in past_reports if r["Timestamp"] != timestamp]

            # Update session data
            request.session["past_reports"] = updated_reports
            request.session.modified = True

            # If current report is being deleted, clear it
            current_report = request.session.get("disease_report", {})
            if current_report.get("Timestamp") == timestamp:
                request.session["disease_report"] = {}
                request.session.modified = True

            # Also delete from database if possible
            try:
                from .models import PlantHealthReport
                # Convert timestamp string to datetime object for database query
                timestamp_format = "%Y-%m-%d %H:%M:%S"
                timestamp_dt = datetime.strptime(timestamp, timestamp_format)
                # Find reports within a small time window (1 second) to account for precision differences
                reports = PlantHealthReport.objects.filter(
                    timestamp__gte=timestamp_dt - timedelta(seconds=1),
                    timestamp__lte=timestamp_dt + timedelta(seconds=1)
                )
                if reports.exists():
                    reports.delete()
            except Exception as e:
                print(f"Error deleting database report: {str(e)}")

            messages.success(request, "Report deleted successfully.")

    return redirect("plant_health_results")


# ─── AI Farming Assistant (Gemini) ────────────────────────────────────────────
@csrf_exempt
@login_required
def ai_chat(request):
    """Gemini-powered farming assistant chat endpoint."""
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            user_message = body.get("message", "").strip()
            if not user_message:
                return JsonResponse({"error": "Empty message"}, status=400)

            gemini_api_key = getattr(settings, "GEMINI_API_KEY", None)
            if not gemini_api_key:
                return JsonResponse({"reply": "AI assistant is not configured. Please contact support."})

            # Add farming context to the system prompt
            system_prompt = (
                "You are AgroBrain AI, an expert agricultural assistant. "
                "You help farmers with crop management, pest control, soil health, irrigation, "
                "weather impact analysis, market trends, and all farming-related queries. "
                "Provide practical, concise, and actionable advice. "
                "Reply in the same language the user writes in."
            )

            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_api_key}"
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": f"{system_prompt}\n\nUser: {user_message}"}
                        ]
                    }
                ]
            }
            response = requests.post(url, json=payload, timeout=30)
            if response.status_code == 200:
                data = response.json()
                reply = data["candidates"][0]["content"]["parts"][0]["text"]
                return JsonResponse({"reply": reply})
            else:
                return JsonResponse({"reply": "I'm having trouble connecting right now. Please try again in a moment."})
        except Exception as e:
            print(f"AI chat error: {e}")
            return JsonResponse({"reply": "An error occurred. Please try again."})
    return JsonResponse({"error": "Method not allowed"}, status=405)


# ─── Crop Recommendation ───────────────────────────────────────────────────────
@login_required
def crop_recommendation(request):
    """AI-powered crop recommendation based on soil/weather input."""
    result = None
    if request.method == "POST":
        soil_type = request.POST.get("soil_type", "")
        ph_level = request.POST.get("ph_level", "")
        region = request.POST.get("region", "")
        season = request.POST.get("season", "")
        rainfall = request.POST.get("rainfall", "")
        temperature = request.POST.get("temperature", "")

        gemini_api_key = getattr(settings, "GEMINI_API_KEY", None)
        if gemini_api_key:
            prompt = (
                f"You are an expert agronomist. Based on the following farm conditions, "
                f"recommend the TOP 5 most suitable crops and explain why each is suitable. "
                f"Also provide basic cultivation tips for each crop.\n\n"
                f"Farm Conditions:\n"
                f"- Soil Type: {soil_type}\n"
                f"- Soil pH: {ph_level}\n"
                f"- Region/Location: {region}\n"
                f"- Season: {season}\n"
                f"- Annual Rainfall: {rainfall} mm\n"
                f"- Average Temperature: {temperature} °C\n\n"
                f"Format your response as:\n"
                f"1. [Crop Name] - Why suitable: ... | Tips: ...\n"
                f"2. [Crop Name] - Why suitable: ... | Tips: ...\n"
                f"(and so on for 5 crops)"
            )
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_api_key}"
                payload = {"contents": [{"parts": [{"text": prompt}]}]}
                response = requests.post(url, json=payload, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    result = data["candidates"][0]["content"]["parts"][0]["text"]
                else:
                    result = "Unable to get AI recommendations at this time. Please try again."
            except Exception as e:
                result = f"Error getting recommendations: {str(e)}"
        else:
            result = "AI service not configured."

    context = {
        "result": result,
        "soil_types": ["Sandy", "Clay", "Loamy", "Silt", "Peat", "Chalky", "Black Cotton", "Red Laterite", "Alluvial"],
        "seasons": ["Kharif (Monsoon)", "Rabi (Winter)", "Zaid (Summer)", "Year-round"],
    }
    return render(request, "myapp/crop_recommendation.html", context)


# ─── Contact Form ──────────────────────────────────────────────────────────────
def contact(request):
    """Contact/feedback form view."""
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        subject = request.POST.get("subject", "").strip()
        message = request.POST.get("message", "").strip()

        if name and email and message:
            # In production, send email here. For now, save to session.
            request.session["contact_submitted"] = True
            messages.success(request, f"Thank you {name}! Your message has been received. We'll respond to {email} shortly.")
            return redirect("contact")
        else:
            messages.error(request, "Please fill in all required fields.")

    return render(request, "myapp/contact.html")


# ─── User Profile ──────────────────────────────────────────────────────────────
@login_required
def profile(request):
    """User profile page."""
    user = request.user
    # Get user's polygons
    user_polygons = Polygon.objects.all()  # Show all polygons for now

    if request.method == "POST":
        # Allow updating first/last name and email
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip()

        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        if email:
            user.email = email
        user.save()
        messages.success(request, "Profile updated successfully!")
        return redirect("profile")

    db_reports = []
    try:
        from .models import PlantHealthReport
        db_reports = PlantHealthReport.objects.filter(user=user).order_by("-timestamp")[:5]
    except Exception:
        pass

    context = {
        "user": user,
        "polygons": user_polygons,
        "db_reports": db_reports,
        "total_reports": len(db_reports),
    }
    return render(request, "myapp/profile.html", context)


# ─── Soil Calculator ───────────────────────────────────────────────────────────
@login_required
def soil_calculator(request):
    """Soil health calculator and fertilizer recommendation tool."""
    result = None
    if request.method == "POST":
        nitrogen = request.POST.get("nitrogen", "0")
        phosphorus = request.POST.get("phosphorus", "0")
        potassium = request.POST.get("potassium", "0")
        ph = request.POST.get("ph", "7")
        crop = request.POST.get("crop", "")

        try:
            n = float(nitrogen)
            p = float(phosphorus)
            k = float(potassium)
            ph_val = float(ph)

            recommendations = []
            # Nitrogen recommendations
            if n < 200:
                recommendations.append(f"🟡 Nitrogen is LOW ({n} kg/ha). Apply Urea (46% N) at 2-3 bags/acre or use compost/green manure.")
            elif n > 400:
                recommendations.append(f"🔴 Nitrogen is HIGH ({n} kg/ha). Reduce nitrogenous fertilizer. Risk of groundwater contamination.")
            else:
                recommendations.append(f"🟢 Nitrogen level is OPTIMAL ({n} kg/ha). Maintain current management.")

            # Phosphorus recommendations
            if p < 10:
                recommendations.append(f"🟡 Phosphorus is LOW ({p} kg/ha). Apply Single Superphosphate (16% P2O5) or DAP at planting.")
            elif p > 50:
                recommendations.append(f"🔴 Phosphorus is HIGH ({p} kg/ha). Avoid phosphorus fertilizers this season.")
            else:
                recommendations.append(f"🟢 Phosphorus level is OPTIMAL ({p} kg/ha).")

            # Potassium recommendations
            if k < 100:
                recommendations.append(f"🟡 Potassium is LOW ({k} kg/ha). Apply Muriate of Potash (60% K2O) at 1-2 bags/acre.")
            elif k > 500:
                recommendations.append(f"🔴 Potassium is HIGH ({k} kg/ha). No K fertilizer needed.")
            else:
                recommendations.append(f"🟢 Potassium level is OPTIMAL ({k} kg/ha).")

            # pH recommendations
            if ph_val < 5.5:
                recommendations.append(f"🔴 Soil is ACIDIC (pH {ph_val}). Apply agricultural lime at 2-4 tonnes/acre to raise pH.")
            elif ph_val > 8.0:
                recommendations.append(f"🔴 Soil is ALKALINE (pH {ph_val}). Apply gypsum or sulfur to lower pH.")
            elif 6.0 <= ph_val <= 7.5:
                recommendations.append(f"🟢 Soil pH is IDEAL ({ph_val}) for most crops.")
            else:
                recommendations.append(f"🟡 Soil pH is slightly off ({ph_val}). Monitor closely.")

            if crop:
                recommendations.append(f"\n🌾 Special note for {crop}: Ensure balanced NPK ratio based on crop's growth stage.")

            result = recommendations
        except ValueError:
            messages.error(request, "Please enter valid numeric values.")

    crops = ["Wheat", "Rice", "Maize", "Cotton", "Sugarcane", "Tomato", "Potato", "Soybean", "Pulses", "Groundnut"]
    return render(request, "myapp/soil_calculator.html", {"result": result, "crops": crops})


# ─── Irrigation Planner ────────────────────────────────────────────────────────
@login_required
def irrigation_planner(request):
    """Smart irrigation scheduling tool."""
    schedule = None
    if request.method == "POST":
        crop_type = request.POST.get("crop_type", "")
        area = request.POST.get("area", "1")
        soil_type = request.POST.get("soil_type", "Loamy")
        growth_stage = request.POST.get("growth_stage", "Vegetative")
        last_irrigation = request.POST.get("last_irrigation", "")

        try:
            area_val = float(area)
            # Water requirement data (liters per hectare per day)
            water_requirements = {
                "Wheat": {"Germination": 400, "Vegetative": 600, "Flowering": 800, "Maturity": 400},
                "Rice": {"Germination": 2000, "Vegetative": 3000, "Flowering": 4000, "Maturity": 2000},
                "Maize": {"Germination": 500, "Vegetative": 700, "Flowering": 900, "Maturity": 500},
                "Cotton": {"Germination": 400, "Vegetative": 600, "Flowering": 800, "Maturity": 400},
                "Tomato": {"Germination": 600, "Vegetative": 800, "Flowering": 1000, "Maturity": 600},
                "Sugarcane": {"Germination": 1500, "Vegetative": 2000, "Flowering": 2500, "Maturity": 1000},
            }

            # Soil retention factor
            soil_factors = {"Sandy": 0.7, "Loamy": 1.0, "Clay": 1.3, "Silt": 1.1, "Black Cotton": 1.4}
            factor = soil_factors.get(soil_type, 1.0)

            base_requirement = water_requirements.get(crop_type, {}).get(growth_stage, 600)
            daily_water = base_requirement * factor * area_val / 1000  # Convert to cubic meters

            schedule = {
                "crop": crop_type,
                "area": area_val,
                "growth_stage": growth_stage,
                "soil_type": soil_type,
                "daily_water_m3": round(daily_water, 2),
                "daily_water_liters": round(daily_water * 1000, 0),
                "weekly_water_m3": round(daily_water * 7, 2),
                "irrigation_frequency": "Every 3-4 days" if soil_type in ["Sandy"] else "Every 5-7 days",
                "best_time": "Early morning (5-8 AM) or evening (6-8 PM)",
                "method": "Drip irrigation recommended for water efficiency" if crop_type in ["Tomato", "Cotton"] else "Sprinkler or flood irrigation",
            }
        except ValueError:
            messages.error(request, "Please enter valid values.")

    crops = ["Wheat", "Rice", "Maize", "Cotton", "Tomato", "Sugarcane", "Potato", "Groundnut"]
    soil_types = ["Sandy", "Loamy", "Clay", "Silt", "Black Cotton"]
    growth_stages = ["Germination", "Vegetative", "Flowering", "Maturity"]
    return render(request, "myapp/irrigation_planner.html", {
        "schedule": schedule, "crops": crops, "soil_types": soil_types, "growth_stages": growth_stages
    })
