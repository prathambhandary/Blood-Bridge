function getLocation() {
  const button = document.querySelector('button[onclick="getLocation()"]');
  const originalText = button.textContent;
  
  // Show loading state
  button.textContent = "⌛ Detecting...";
  button.disabled = true;

  if (!navigator.geolocation) {
    button.textContent = "❌ No GPS Support";
    setTimeout(() => resetButton(button, originalText), 2000);
    return;
  }

  navigator.geolocation.getCurrentPosition(
    (position) => {
      updateLocation(position.coords.latitude, position.coords.longitude);
      button.textContent = "✓ Location Set!";
      setTimeout(() => resetButton(button, originalText), 1500);
    },
    (error) => {
      handleLocationError(error, button, originalText);
    },
    {
      enableHighAccuracy: true,
      timeout: 8000,  // Slightly shorter timeout for mobile
      maximumAge: 15000  // Accept slightly older cached locations
    }
  );
}

// Helper: Update map & inputs (no changes)
function updateLocation(lat, lng) {
  document.getElementById('latitude').value = lat.toFixed(6);
  document.getElementById('longitude').value = lng.toFixed(6);
  map.setView([lat, lng], 15);
  marker.setLatLng([lat, lng]);
}

// Helper: Reset button state (no changes)
function resetButton(button, text) {
  button.textContent = text;
  button.disabled = false;
}

// Helper: Silent error handling (no alerts)
function handleLocationError(error, button, originalText) {
  switch (error.code) {
    case error.PERMISSION_DENIED:
      button.textContent = "📍 Allow Access";
      break;
    case error.POSITION_UNAVAILABLE:
      button.textContent = "🚫 No Signal";
      break;
    case error.TIMEOUT:
      button.textContent = "⌛ Time Out";
      // Silent fallback attempt
      getLocationWithFallback();
      break;
    default:
      button.textContent = "❌ Error";
  }
  setTimeout(() => resetButton(button, originalText), 2000);
}

// Fallback: Silent retry
function getLocationWithFallback() {
  navigator.geolocation.getCurrentPosition(
    (position) => updateLocation(position.coords.latitude, position.coords.longitude),
    () => {}, // Completely silent on failure
    { enableHighAccuracy: false, timeout: 4000 }
  );
}