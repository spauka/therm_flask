// (c) 2025 Sebsatian Pauka
// This code is licensed under MIT license (see LICENSE file for details)

var smartApp = angular.module('smartApp', [
    'ngRoute',
    'ui.bootstrap',
    'app.controllers',
    'app.main',
    'app.navigation',
]);

smartApp.config(['$routeProvider', function ($routeProvider) {
    $routeProvider
        .when('/', {
            redirectTo: '/dashboard'
        })
        .when('/dashboard', {
            templateUrl: function ($routeParams) {
                return 'views/dashboard.html';
            },
            controller: 'SmartAppController',
        })
        .when('/:fridge', {
            templateUrl: function ($routeParams) {
                return 'views/fridge-separate.html';
            },
            controller: 'FridgeViewController'
        })
        .when('/:fridge/:supp', {
            templateUrl: function ($routeParams) {
                return 'views/fridge-separate.html';
            },
            controller: 'FridgeViewController'
        })
        .otherwise({
            redirectTo: '/dashboard'
        });
}]);

smartApp.run(['$rootScope', function ($rootScope) {
}])
