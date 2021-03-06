angular.module('pixelmatrix-app').config(['$locationProvider', '$routeProvider', '$httpProvider', function config ($locationProvider, $routeProvider, $httpProvider) {
    $locationProvider.hashPrefix('!');
    
    // Set http interceptor to handle auth
    $httpProvider.interceptors.push('authHandler');   

    // Configure routes here
    $routeProvider
        .when('/login', {
            template: '<login></login>'
        })
        .when('/', {
            template: '<home></home>',
        })
        .when('/brightness', {
            template: '<brightness></brightness>',
        })
        .when('/configuration', {
            template: '<configuration></configuration>',
        })
        .otherwise('/');
}]);
