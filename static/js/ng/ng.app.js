var smartApp = angular.module('smartApp', [
    'ngRoute',
    //'ngAnimate', // this is buggy, jarviswidget will not work with ngAnimate :(
    'ui.bootstrap',
    'app.controllers',
    'app.main',
    'app.navigation',
    'app.localize',
    'app.activity',
    'app.smartui'
]);

smartApp.config(['$routeProvider', '$provide', function($routeProvider, $provide) {
  $routeProvider
    .when('/', {
      redirectTo: '/dashboard'
    })
    .when('/dashboard', {
      templateUrl: function($routeParams) {
        return 'views/dashboard.html';
      },
      controller: 'FridgeViewController'
    })
   .when('/:fridge', {
      templateUrl: function($routeParams) {
        return 'views/fridge-separate.html';
      },
      controller: 'FridgeViewController'
    })
    .when('/:fridge/combined', {
      templateUrl: function($routeParams) {
        return 'views/fridge-combined.html';
      },
      controller: 'FridgeViewController'
    })
    .when('/:fridge/historic', {
      templateUrl: function($routeParams) {
        return 'views/fridge-historic.html';
      },
      controller: 'FridgeViewController'
    })
    .when('/:fridge/:supp', {
      templateUrl: function($routeParams) {
        return 'views/fridge-separate.html';
      },
    controller: 'FridgeViewController'
    })
    .when('/:fridge/:supp/historic', {
      templateUrl: function($routeParams) {
        return 'views/fridge-historic.html';
      },
      controller: 'FridgeViewController'
    })
    .otherwise({
      redirectTo: '/dashboard'
    });

  // with this, you can use $log('Message') same as $log.info('Message');
  $provide.decorator('$log', ['$delegate',
  function($delegate) {
    // create a new function to be returned below as the $log service (instead of the $delegate)
    function logger() {
      // if $log fn is called directly, default to "info" message
      logger.info.apply(logger, arguments);
    }

    // add all the $log props into our new logger fn
    angular.extend(logger, $delegate);
    return logger;
  }]); 

}]);

smartApp.run(['$rootScope', 'settings', function($rootScope, settings) {
}])
