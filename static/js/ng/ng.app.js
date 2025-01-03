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
            controller: 'FridgeViewController'
        })
        .when('/:fridge', {
            templateUrl: function ($routeParams) {
                return 'views/fridge-separate.html';
            },
            controller: 'FridgeViewController'
        })
        .when('/:fridge/combined', {
            templateUrl: function ($routeParams) {
                return 'views/fridge-combined.html';
            },
            controller: 'FridgeViewController'
        })
        .when('/:fridge/historic', {
            templateUrl: function ($routeParams) {
                return 'views/fridge-historic.html';
            },
            controller: 'FridgeViewController'
        })
        .when('/:fridge/:supp', {
            templateUrl: function ($routeParams) {
                return 'views/fridge-separate.html';
            },
            controller: 'FridgeViewController'
        })
        .when('/:fridge/:supp/historic', {
            templateUrl: function ($routeParams) {
                return 'views/fridge-historic.html';
            },
            controller: 'FridgeViewController'
        })
        .otherwise({
            redirectTo: '/dashboard'
        });
}]);

smartApp.run(['$rootScope', 'settings', function ($rootScope, settings) {
}])
