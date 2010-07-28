(function($){
    var Location = {
        supportsGeoLocation: function() {
            return !! navigator.geolocation;
        },
        watch: function(callback) {
            if (this.supportsGeoLocation()) {
                
                var options = {
                    enableHighAccuracy: true
                };

                var watchId = navigator.geolocation.watchPosition(function(position) {
                    // TODO: do some massaging / standardization?
                    console.log("location", position);
                    callback(position);
                }, /* TODO */ function(error) {console.error(error)}, options);
                return watchId;
            } else {
                // Fall back to GeoIP
                return null;
            }
        },
        clearWatch: function(watchId) {
            if (this.supportsGeoLocation()) {
                return navigator.geolocation.clearWatch(watchId);
            }
            return null;
        }
    }

    window.simplegeo = {
        Location: Location
    }
})(jQuery);
