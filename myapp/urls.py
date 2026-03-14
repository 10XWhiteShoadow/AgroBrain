from django.urls import path
from . import views



urlpatterns = [
    # Market route is now handled by the market app
    # path('market/', views.market, name='market'),  # Commented out to avoid conflict
    # Core routes
    path('', views.dashboard, name='dashboard'),
    
    # Authentication routes
    path('login/', views.login_page, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Application routes
    path('services/', views.services, name='services'),
    path('tools/', views.Tool, name='tools'),
    path('about/', views.about, name='about'),
    path('resources/', views.resources_view, name='resources'),
    path('trade/', views.trade, name='trade'),
    path('privacy/', views.privacy, name='privacy'),
    path('TandC/', views.TandC, name='TandC'),
    path('FAQs/', views.FAQs, name='FAQs'),
    path('weather/', views.weather_dashboard, name='weather'),
    path('contact/', views.contact, name='contact'),
    path('profile/', views.profile, name='profile'),
    
    # Polygon-related routes
    path('add_polygon/', views.add_polygon, name='add_polygon'),
    path('polygons/', views.polygon_list, name='polygon_list'),
    path('agro_data/<str:polygon_id>/', views.get_agro_data, name='get_agro_data'),
    path('details/<str:polygon_id>/', views.details, name='details'),
    
    # Additional features
    path('news/', views.news, name='news'),
    path("plant-health/", views.detect_disease, name="plant_health"),
    path("plant-health/detect/", views.detect_disease, name="plant_disease_detection"),
    path('plant-health/results/', views.plant_health_results, name='plant_health_results'),
    path('plant-health/download/', views.download_report, name='download_pdf'),
    path("plant-health/results/delete/", views.delete_report, name="delete_report"),
    path("plant-health/results/delete/<str:timestamp>/", views.delete_report, name="delete_report_with_timestamp"),
    
    # AI & Smart Farming Tools
    path('ai-chat/', views.ai_chat, name='ai_chat'),
    path('crop-recommendation/', views.crop_recommendation, name='crop_recommendation'),
    path('soil-calculator/', views.soil_calculator, name='soil_calculator'),
    path('irrigation-planner/', views.irrigation_planner, name='irrigation_planner'),
]
