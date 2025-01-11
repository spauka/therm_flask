/*         ______________________________________
  ________|                                      |_______
  \       |           SmartAdmin WebApp          |      /
   \      |      Copyright © 2014 MyOrange       |     /
   /      |______________________________________|     \
  /__________)                                (_________\

 * The above copyright notice and this permission notice shall be
 * included in all copies or substantial portions of the Software.
 * =======================================================================
 * SmartAdmin is FULLY owned and LICENSED by MYORANGE INC.
 * This script may NOT be RESOLD or REDISTRUBUTED under any
 * circumstances, and is only to be used with this purchased
 * copy of SmartAdmin Template.
 * =======================================================================
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
 * MERCHANTABILITY, IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
 * LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
 * OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
 * WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 * =======================================================================
 * author: Sunny (@bootstraphunt)
 * email: info@myorange.ca
 */

// APP DIRECTIVES
// main directives
angular.module('app.main', [])
    // initiate body
    .directive('body', function () {
        return {
            restrict: 'E',
            link: function (scope, element, attrs) {
                element.on('click', 'a[href="#"], [data-toggle]', function (e) {
                    e.preventDefault();
                })
            }
        }
    })

    .factory('ribbon', ['$rootScope', function ($rootScope) {
        var ribbon = {
            currentBreadcrumb: [],
            updateBreadcrumb: function (crumbs) {
                crumbs.push('Home');
                var breadCrumb = crumbs.reverse();
                ribbon.currentBreadcrumb = breadCrumb;
                $rootScope.$broadcast('navItemSelected', breadCrumb);
            }
        };

        return ribbon;
    }])

    .directive('action', function () {
        return {
            restrict: 'A',
            link: function (scope, element, attrs) {
                /*
                 * SMART ACTIONS
                 */
                var smartActions = {

                    // LAUNCH FULLSCREEN
                    launchFullscreen: function (element) {

                        if (!$('body').hasClass("full-screen")) {

                            $('body').addClass("full-screen");

                            if (element.requestFullscreen) {
                                element.requestFullscreen();
                            } else if (element.mozRequestFullScreen) {
                                element.mozRequestFullScreen();
                            } else if (element.webkitRequestFullscreen) {
                                element.webkitRequestFullscreen();
                            } else if (element.msRequestFullscreen) {
                                element.msRequestFullscreen();
                            }

                        } else {

                            $('body').removeClass("full-screen");

                            if (document.exitFullscreen) {
                                document.exitFullscreen();
                            } else if (document.mozCancelFullScreen) {
                                document.mozCancelFullScreen();
                            } else if (document.webkitExitFullscreen) {
                                document.webkitExitFullscreen();
                            }

                        }

                    },

                    // MINIFY MENU
                    minifyMenu: function ($this) {
                        if (!$('body').hasClass("menu-on-top")) {
                            $('body').toggleClass("minified");
                            $('body').removeClass("hidden-menu");
                            $('html').removeClass("hidden-menu-mobile-lock");
                            $this.effect("highlight", {}, 500);
                        }
                    },

                    // TOGGLE MENU
                    toggleMenu: function () {
                        if (!$('body').hasClass("menu-on-top")) {
                            $('html').toggleClass("hidden-menu-mobile-lock");
                            $('body').toggleClass("hidden-menu");
                            $('body').removeClass("minified");
                        } else if ($('body').hasClass("menu-on-top") && $('body').hasClass("mobile-view-activated")) {
                            $('html').toggleClass("hidden-menu-mobile-lock");
                            $('body').toggleClass("hidden-menu");
                            $('body').removeClass("minified");
                        }
                    }
                };

                var actionEvents = {
                    launchFullscreen: function (e) {
                        smartActions.launchFullscreen(document.documentElement);
                    },
                    minifyMenu: function (e) {
                        smartActions.minifyMenu(element);
                    },
                    toggleMenu: function (e) {
                        smartActions.toggleMenu();
                    },
                };

                if (angular.isDefined(attrs.action) && attrs.action != '') {
                    var actionEvent = actionEvents[attrs.action];
                    if (typeof actionEvent === 'function') {
                        element.on('click', function (e) {
                            actionEvent(e);
                            e.preventDefault();
                        });
                    }
                }

            }
        };
    })

    .directive('header', function () {
        return {
            restrict: 'EA',
            link: function (scope, element, attrs) {
                // SHOW & HIDE MOBILE SEARCH FIELD
                angular.element('#search-mobile').on("click", function () {
                    $('body').addClass('search-mobile');
                });

                angular.element('#cancel-search-js').on("click", function () {
                    $('body').removeClass('search-mobile');
                });
            }
        };
    })

    .controller('breadcrumbController', ['$scope', function ($scope) {
        $scope.breadcrumbs = [];
        $scope.$on('navItemSelected', function (name, crumbs) {
            $scope.setBreadcrumb(crumbs);
        });

        $scope.setBreadcrumb = function (crumbs) {
            $scope.breadcrumbs = crumbs;
        }
    }])

    .directive('breadcrumb', ['ribbon', '$compile', function (ribbon, $compile) {
        return {
            restrict: 'AE',
            controller: 'breadcrumbController',
            replace: true,
            link: function (scope, element, attrs) {
                scope.$watch('breadcrumbs', function (newVal, oldVal) {
                    scope.updateDOM();
                    if (newVal !== oldVal) {
                        // update DOM
                        scope.updateDOM();
                    }
                })
                scope.updateDOM = function () {
                    element.empty();
                    angular.forEach(scope.breadcrumbs, function (crumb) {
                        var li = angular.element('<li>' + crumb + '</li>');

                        $compile(li)(scope);
                        element.append(li);
                    });
                };

                // set the current breadcrumb on load
                scope.setBreadcrumb(ribbon.currentBreadcrumb);
                scope.updateDOM();
            },
            template: '<ol class="breadcrumb"></ol>'
        }
    }]);

// directives for navigation
angular.module('app.navigation', [])
    .directive('navigation', function () {
        return {
            restrict: 'AE',
            controller: ['$scope', function ($scope) {

            }],
            transclude: true,
            replace: true,
            link: function (scope, element, attrs) {
                if (!topmenu) {
                    if (!null) {
                        element.first().jarvismenu({
                            accordion: true,
                            speed: $.menu_speed,
                            closedSign: '<em class="fa-solid fa-square-plus"></em>',
                            openedSign: '<em class="fa-solid fa-square-minus"></em>'
                        });
                    } else {
                        alert("Error - menu anchor does not exist");
                    }
                }

                // SLIMSCROLL FOR NAV
                if ($.fn.slimScroll) {
                    element.slimScroll({
                        height: '100%'
                    });
                }

                scope.getElement = function () {
                    return element;
                }
            },
            template: '<nav><ul data-ng-transclude=""></ul></nav>'
        };
    })

    .controller('NavGroupController', ['$scope', function ($scope) {
        $scope.active = false;
        $scope.hasIcon = angular.isDefined($scope.icon);
        $scope.hasIconCaption = angular.isDefined($scope.iconCaption);

        this.setActive = function (active) {
            $scope.active = active;
        }

    }])
    .directive('navGroup', function () {
        return {
            restrict: 'AE',
            controller: 'NavGroupController',
            transclude: true,
            replace: true,
            scope: {
                icon: '@',
                title: '@',
                iconCaption: '@',
                active: '=?'
            },
            template: '\
        <li data-ng-class="{active: active}">\
          <a href="">\
            <i data-ng-if="hasIcon" class="{{ icon }}"><em data-ng-if="hasIconCaption"> {{ iconCaption }} </em></i>\
            <span class="menu-item-parent">{{ title }}</span>\
          </a>\
          <ul data-ng-transclude=""></ul>\
        </li>',

        };
    })

    .controller('NavItemController', ['$rootScope', '$scope', '$location', function ($rootScope, $scope, $location) {
        $scope.isChild = false;
        $scope.active = false;
        $scope.isActive = function (viewLocation) {
            $scope.active = viewLocation === $location.path();
            return $scope.active;
        };

        $scope.hasIcon = angular.isDefined($scope.icon);
        $scope.hasIconCaption = angular.isDefined($scope.iconCaption);

        $scope.getItemUrl = function (view) {
            if (angular.isDefined($scope.href)) return $scope.href;
            if (!angular.isDefined(view)) return '';
            return "#!" + view;
        };

        $scope.getItemTarget = function () {
            return angular.isDefined($scope.target) ? $scope.target : '_self';
        };

    }])
    .directive('navItem', ['ribbon', '$window', function (ribbon, $window) {
        return {
            require: ['^navigation', '^?navGroup'],
            restrict: 'AE',
            controller: 'NavItemController',
            scope: {
                title: '@',
                view: '@',
                icon: '@',
                iconCaption: '@',
                href: '@',
                target: '@'
            },
            link: function (scope, element, attrs, parentCtrls) {
                var navCtrl = parentCtrls[0],
                    navgroupCtrl = parentCtrls[1];

                scope.$watch('active', function (newVal, oldVal) {
                    if (newVal) {
                        if (angular.isDefined(navgroupCtrl) && navgroupCtrl !== null) navgroupCtrl.setActive(true);
                        $window.document.title = scope.title;
                        scope.setBreadcrumb();
                    } else {
                        if (angular.isDefined(navgroupCtrl) && navgroupCtrl !== null) navgroupCtrl.setActive(false);
                    }
                });

                scope.openParents = scope.isActive(scope.view);
                scope.isChild = angular.isDefined(navgroupCtrl) && navgroupCtrl !== null;

                scope.setBreadcrumb = function () {
                    var crumbs = [];
                    crumbs.push(scope.title);
                    // get parent menus
                    element.parents('nav li').each(function () {
                        var el = angular.element(this);
                        var parent = el.find('.menu-item-parent:eq(0)');
                        crumbs.push(parent.text().trim());
                        if (scope.openParents) {
                            // open menu on first load
                            parent.trigger('click');
                        }
                    });
                    // this should be only fired upon first load so let's set this to false now
                    scope.openParents = false;
                    ribbon.updateBreadcrumb(crumbs);
                };

                element.on('click', 'a[href!="#"]', function () {
                    if ($('body').hasClass('mobile-view-activated')) {
                        $('body').removeClass('hidden-menu');
                        $('html').removeClass("hidden-menu-mobile-lock");
                    }
                });

            },
            transclude: true,
            replace: true,
            template: '\
        <li data-ng-class="{active: isActive(view)}">\
          <a href="{{ getItemUrl(view) }}" target="{{ getItemTarget() }}" title="{{ title }}">\
            <i data-ng-if="hasIcon" class="{{ icon }}"><em data-ng-if="hasIconCaption"> {{ iconCaption }} </em></i>\
            <span ng-class="{\'menu-item-parent\': !isChild}"> {{ title }} </span>\
            <span data-ng-transclude=""></span>\
          </a>\
        </li>'
        };
    }]);
