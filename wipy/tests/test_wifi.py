def test_wifi_connection():
    from lib.wifi_manager import WiFiManager
    
    wifi = WiFiManager("test_ssid", "test_pass")
    assert wifi.ssid == "test_ssid"
    # Plus de tests... 