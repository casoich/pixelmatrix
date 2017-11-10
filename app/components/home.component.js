angular.module('pixelmatrix-app').component('home', {
    templateUrl: '/templates/home.template.html',
    controller: ['$scope', 
    '$rootScope', 
    '$http', 
    '$location', 
    '$interval', 
    '$sce', 
    function HomeController ($scope, $rootScope, $http, $location, $interval, $sce) {
        var self = this;


        $scope.shows = [
            {
                name:"Rainbow",
                argument:"rainbow",
                paramVisibility: {
                  brightness:true,
                  saturation:false,
                  hue:false,
                  hue2:false,
                  count:false,
                  speed:true,
                  offset:false
                }
            },
            {
                name:"Blank",
                argument:"blank",
                paramVisibility: {
                  brightness:false,
                  saturation:false,
                  hue:false,
                  hue2:false,
                  count:false,
                  speed:false,
                  offset:false
                }

            },
            {
                name:"Flurry",
                argument:"flurry",
                paramVisibility: {
                  brightness:true,
                  saturation:true,
                  hue:true,
                  hue2:true,
                  count:true,
                  speed:true,
                  offset:false
                }

            },
            {
                name:"Scurry",
                argument:"scurry",
                paramVisibility: {
                  brightness:true,
                  saturation:true,
                  hue:true,
                  hue2:false,
                  count:true,
                  speed:true,
                  offset:true
                }

            },
            {
                name:"Rainbow Stripes",
                argument:"wheelbuster",
                paramVisibility: {
                  brightness:true,
                  saturation:false,
                  hue:false,
                  hue2:false,
                  count:true,
                  speed:true,
                  offset:false
                }

            },
            {
                name:"Twinkle",
                argument:"twinkle",
                paramVisibility: {
                  brightness:true,
                  saturation:true,
                  hue:true,
                  hue2:false,
                  count:true,
                  speed:true,
                  offset:false
                }


            },
            {
                name:"Dazzle",
                argument:"superwhite",
                paramVisibility: {
                  brightness:true,
                  saturation:false,
                  hue:false,
                  hue2:false,
                  count:true,
                  speed:true,
                  offset:false
                }

            }
        ];
        if (!$scope.params) {
    $scope.params={
        argument:"scurry",
        brightness:"255",
        saturation:"100",
        hue:"26",
        hue2:"128",
        count:"67",
        speed:"100",
        offset:"50"
    };
          
        }


        $scope.dropboxitemselected = function (item) {

            $scope.currentShow = item;
            $scope.params['argument']=item.argument;
            $scope.pushParams($scope.params)
            console.log(item);
        }
        $scope.isAdminUser = function(){
         return $rootScope.isAdmin;
     }

     $scope.$watch('active', function () {
            //getMaxFeedUnits($scope.carousel.slides[$scope.active]);
            console.log('Slide ' + $scope.active + ' is active');
        });
    $scope.$watch('params',function() {
        console.log($scope.params);
        $scope.pushParams($scope.params);
    }, true);

    $scope.pushParams = function pushParams(params) {
      $http.post('/param',{params:params}).then(function pushParamsSuccess () {
            //console.log("pushParamsSuccess");
        });
    }
function getparams (){
  console.log("home.component is doing getparams()");
    $http.get('/param').then(function(response){
            //alert(response.data.max);
            console.log("home component getparams got:",JSON.stringify(response));
        $scope.params=response;

        });
}

self.$onInit = function init () {
            console.log("got to self.onInit");
getparams();
    $http.get('/wtf').then(function (response) {
        if (response.status === 200 && response.data) {
          console.log("the /wtf response was ok:",response.status,response.data);

            for (var i = 0; i < response.data.length; i++) {
                for (var j = 0; j < $scope.configurations.length; j++) {
                    if (response.data[i]._id === $scope.configurations[j].name) {
                        $scope.configurations[j].ipAddress = response.data[i].ipAddress;
                    }
                }
            }

                } else {
                   console.log("the /wtf response was weird:",JSON.stringify(response));

                }
            });
};

$scope.$on('$locationChangeStart', function (event, next, current) {
    if (interval) {
        $interval.cancel(interval);
        interval = null;
    }
});

function getIP (slide) {
    var active = slide ? slide.id : $scope.active;

    if (active === 1) {
        for (var i = 0; i < $scope.configurations.length; i++) {
            if ($scope.configurations[i].name === 'Pi 1') {
                return $scope.configurations[i].ipAddress;
            }
        }
    } else if (active === 2) {
        for (var j = 0; j < $scope.configurations.length; j++) {
            if ($scope.configurations[j].name === 'Pi 2') {
                return $scope.configurations[j].ipAddress;
            }
        }
    }

    return window.location.hostname;
}

}]
});
