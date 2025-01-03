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

                    // LOGOUT MSG 
                    userLogout: function ($this) {

                        // ask verification
                        $.SmartMessageBox({
                            title: "<i class='fa-solid fa-right-from-bracket txt-color-orangeDark'></i> Logout <span class='txt-color-orangeDark'><strong>" + $('#show-shortcut').text() + "</strong></span> ?",
                            content: $this.data('logout-msg') || "You can improve your security further after logging out by closing this opened browser",
                            buttons: '[No][Yes]'

                        }, function (ButtonPressed) {
                            if (ButtonPressed == "Yes") {
                                $('body').addClass('animated fadeOutUp');
                                setTimeout(logout, 1000);
                            }
                        });
                        function logout() {
                            window.location = $this.attr('href');
                        }

                    },

                    // RESET WIDGETS
                    resetWidgets: function ($this) {
                        $.widresetMSG = $this.data('reset-msg');

                        $.SmartMessageBox({
                            title: "<i class='fa-solid fa-arrows-rotate' style='color:green'></i> Clear Local Storage",
                            content: $.widresetMSG || "Would you like to RESET all your saved widgets and clear LocalStorage?",
                            buttons: '[No][Yes]'
                        }, function (ButtonPressed) {
                            if (ButtonPressed == "Yes" && localStorage) {
                                localStorage.clear();
                                location.reload();
                            }

                        });
                    },

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
                    },

                    // TOGGLE SHORTCUT 
                    toggleShortcut: function () {

                        if (shortcut_dropdown.is(":visible")) {
                            shortcut_buttons_hide();
                        } else {
                            shortcut_buttons_show();
                        }

                        // SHORT CUT (buttons that appear when clicked on user name)
                        shortcut_dropdown.find('a').on("click", function (e) {
                            e.preventDefault();
                            window.location = $(this).attr('href');
                            setTimeout(shortcut_buttons_hide, 300);

                        });

                        // SHORTCUT buttons goes away if mouse is clicked outside of the area
                        $(document).mouseup(function (e) {
                            if (!shortcut_dropdown.is(e.target) && shortcut_dropdown.has(e.target).length === 0) {
                                shortcut_buttons_hide();
                            }
                        });

                        // SHORTCUT ANIMATE HIDE
                        function shortcut_buttons_hide() {
                            shortcut_dropdown.animate({
                                height: "hide"
                            }, 300, "easeOutCirc");
                            $('body').removeClass('shortcut-on');

                        }

                        // SHORTCUT ANIMATE SHOW
                        function shortcut_buttons_show() {
                            shortcut_dropdown.animate({
                                height: "show"
                            }, 200, "easeOutCirc");
                            $('body').addClass('shortcut-on');
                        }

                    }

                };

                var actionEvents = {
                    userLogout: function (e) {
                        smartActions.userLogout(element);
                    },
                    resetWidgets: function (e) {
                        smartActions.resetWidgets(element);
                    },
                    launchFullscreen: function (e) {
                        smartActions.launchFullscreen(document.documentElement);
                    },
                    minifyMenu: function (e) {
                        smartActions.minifyMenu(element);
                    },
                    toggleMenu: function (e) {
                        smartActions.toggleMenu();
                    },
                    toggleShortcut: function (e) {
                        smartActions.toggleShortcut();
                    }
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

    .directive('ribbon', function () {
        return {
            restrict: 'A',
            link: function (scope, element, attrs) {

                // hide bg options
                var smartbgimage = "<h6 class='margin-top-10 semi-bold'>Background</h6><img src='img/pattern/graphy-xs.png' data-htmlbg-url='img/pattern/graphy.png' width='22' height='22' class='margin-right-5 bordered cursor-pointer'><img src='img/pattern/tileable_wood_texture-xs.png' width='22' height='22' data-htmlbg-url='img/pattern/tileable_wood_texture.png' class='margin-right-5 bordered cursor-pointer'><img src='img/pattern/sneaker_mesh_fabric-xs.png' width='22' height='22' data-htmlbg-url='img/pattern/sneaker_mesh_fabric.png' class='margin-right-5 bordered cursor-pointer'><img src='img/pattern/nistri-xs.png' data-htmlbg-url='img/pattern/nistri.png' width='22' height='22' class='margin-right-5 bordered cursor-pointer'><img src='img/pattern/paper-xs.png' data-htmlbg-url='img/pattern/paper.png' width='22' height='22' class='bordered cursor-pointer'>";
                $("#smart-bgimages")
                    .fadeOut();

                /*
                 * FIXED HEADER
                 */
                $('input[type="checkbox"]#smart-fixed-header')
                    .on("click", function () {
                        if ($(this)
                            .is(':checked')) {
                            //checked
                            $('body').addClass("fixed-header");
                        } else {
                            //unchecked
                            $('input[type="checkbox"]#smart-fixed-ribbon')
                                .prop('checked', false);
                            $('input[type="checkbox"]#smart-fixed-navigation')
                                .prop('checked', false);

                            $('body').removeClass("fixed-header");
                            $('body').removeClass("fixed-navigation");
                            $('body').removeClass("fixed-ribbon");

                        }
                    });

                /*
                 * FIXED NAV
                 */
                $('input[type="checkbox"]#smart-fixed-navigation')
                    .on("click", function () {
                        if ($(this)
                            .is(':checked')) {
                            //checked
                            $('input[type="checkbox"]#smart-fixed-header')
                                .prop('checked', true);

                            $('body').addClass("fixed-header");
                            $('body').addClass("fixed-navigation");

                            $('input[type="checkbox"]#smart-fixed-container')
                                .prop('checked', false);
                            $('body').removeClass("container");

                        } else {
                            //unchecked
                            $('input[type="checkbox"]#smart-fixed-ribbon')
                                .prop('checked', false);
                            $('body').removeClass("fixed-navigation");
                            $('body').removeClass("fixed-ribbon");
                        }
                    });

                /*
                 * FIXED RIBBON
                 */
                $('input[type="checkbox"]#smart-fixed-ribbon')
                    .on("click", function () {
                        if ($(this)
                            .is(':checked')) {

                            //checked
                            $('input[type="checkbox"]#smart-fixed-header')
                                .prop('checked', true);
                            $('input[type="checkbox"]#smart-fixed-navigation')
                                .prop('checked', true);
                            $('input[type="checkbox"]#smart-fixed-ribbon')
                                .prop('checked', true);

                            //apply
                            $('body').addClass("fixed-header");
                            $('body').addClass("fixed-navigation");
                            $('body').addClass("fixed-ribbon");

                            $('input[type="checkbox"]#smart-fixed-container')
                                .prop('checked', false);
                            $('body').removeClass("container");

                        } else {
                            //unchecked
                            $('body').removeClass("fixed-ribbon");
                        }
                    });

                /*
                 * RTL SUPPORT
                 */
                $('input[type="checkbox"]#smart-fixed-footer')
                    .on("click", function () {
                        if ($(this)
                            .is(':checked')) {

                            //checked
                            $('body').addClass("fixed-page-footer");

                        } else {
                            //unchecked
                            $('body').removeClass("fixed-page-footer");
                        }
                    });


                /*
                 * RTL SUPPORT
                 */
                $('input[type="checkbox"]#smart-rtl')
                    .on("click", function () {
                        if ($(this)
                            .is(':checked')) {

                            //checked
                            $('body').addClass("smart-rtl");

                        } else {
                            //unchecked
                            $('body').removeClass("smart-rtl");
                        }
                    });

                /*
                 * MENU ON TOP
                 */

                $('#smart-topmenu')
                    .on('change', function (e) {
                        if ($(this)
                            .prop('checked')) {
                            //window.location.href = '?menu=top';
                            localStorage.setItem('sm-setmenu', 'top');
                            location.reload();
                        } else {
                            //window.location.href = '?';
                            localStorage.setItem('sm-setmenu', 'left');
                            location.reload();
                        }
                    });

                if (localStorage.getItem('sm-setmenu') == 'top') {
                    $('#smart-topmenu')
                        .prop('checked', true);
                } else {
                    $('#smart-topmenu')
                        .prop('checked', false);
                }

                /*
                 * INSIDE CONTAINER
                 */
                $('input[type="checkbox"]#smart-fixed-container')
                    .on("click", function () {
                        if ($(this)
                            .is(':checked')) {
                            //checked
                            $('body').addClass("container");

                            $('input[type="checkbox"]#smart-fixed-ribbon')
                                .prop('checked', false);
                            $('body').removeClass("fixed-ribbon");

                            $('input[type="checkbox"]#smart-fixed-navigation')
                                .prop('checked', false);
                            $('body').removeClass("fixed-navigation");

                            if (smartbgimage) {
                                $("#smart-bgimages")
                                    .append(smartbgimage)
                                    .fadeIn(1000);
                                $("#smart-bgimages img")
                                    .bind("click", function () {
                                        var $this = $(this);
                                        var $html = $('html')
                                        bgurl = ($this.data("htmlbg-url"));
                                        $html.css("background-image", "url(" + bgurl + ")");
                                    })
                                smartbgimage = null;
                            } else {
                                $("#smart-bgimages")
                                    .fadeIn(1000);
                            }

                        } else {
                            //unchecked
                            $('body').removeClass("container");
                            $("#smart-bgimages")
                                .fadeOut();
                        }
                    });

                /*
                 * REFRESH WIDGET
                 */
                $("#reset-smart-widget")
                    .on("click", function () {
                        $('#refresh')
                            .click();
                        return false;
                    });

                /*
                 * STYLES
                 */
                $("#smart-styles > a")
                    .on('click', function () {
                        var $this = $(this);
                        var $logo = $("#logo img");
                        $('body').removeClassPrefix('smart-style')
                            .addClass($this.attr("id"));
                        $logo.attr('src', $this.data("skinlogo"));
                        $("#smart-styles > a #skin-checked")
                            .remove();
                        $this.prepend("<i class='fa-solid fa-check fa-fw' id='skin-checked'></i>");
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
    }])
    ;

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
    }])
    ;

// directives for activity
angular.module('app.activity', [])
    .controller('ActivityController', ['$scope', '$http', function ($scope, $http) {
        var ctrl = this,
            items = ctrl.items = $scope.items = [];

        ctrl.loadItem = function (loadedItem, callback) {
            angular.forEach(items, function (item) {
                if (item.active && item !== loadedItem) {
                    item.active = false;
                    //item.onDeselect();
                }
            });

            loadedItem.active = true;
            if (angular.isDefined(loadedItem.onLoad)) {
                loadedItem.onLoad(loadedItem);
            }

            $http.get(loadedItem.src).then(function (result) {
                var content = result.data;
                if (angular.isDefined(callback)) {
                    callback(content);
                }
            });
        };

        ctrl.addItem = function (item) {
            items.push(item);
            if (!angular.isDefined(item.active)) {
                // set the default
                item.active = false;
            } else if (item.active) {
                ctrl.loadItem(item);
            }
        };

        ctrl.refresh = function (e) {
            var btn = angular.element(e.currentTarget);
            btn.button('loading');

            if (angular.isDefined($scope.onRefresh)) {
                $scope.onRefresh($scope, function () {
                    btn.button('reset');
                });
            } else {
                btn.button('reset');
            }
        };
    }])

    .directive('activity', function () {
        return {
            restrict: 'AE',
            replace: true,
            transclude: true,
            controller: 'ActivityController',
            scope: {
                onRefresh: '=onrefresh',
            },
            template: '<span data-ng-transclude=""></span>'
        };
    })

    .directive('activityButton', function () {
        return {
            restrict: 'AE',
            require: '^activity',
            replace: true,
            transclude: true,
            controller: function ($scope) {

            },
            scope: {
                icon: '@',
                total: '='
            },
            template: '\
          <span id="activity" class="activity-dropdown">\
            <i ng-class="icon"></i>\
            <b class="badge"> {{ total }} </b>\
          </span>',
            link: function (scope, element, attrs, activityCtrl) {

                attrs.$observe('icon', function (value) {
                    if (!angular.isDefined(value))
                        scope.icon = 'fa-solid fa-user';
                });

                element.on('click', function (e) {
                    var $this = $(this);

                    if ($this.find('.badge').hasClass('bg-color-red')) {
                        $this.find('.badge').removeClassPrefix('bg-color-');
                        $this.find('.badge').text("0");
                        // console.log("Ajax call for activity")
                    }

                    if (!$this.next('.ajax-dropdown').is(':visible')) {
                        $this.next('.ajax-dropdown').fadeIn(150);
                        $this.addClass('active');
                    } else {
                        $this.next('.ajax-dropdown').fadeOut(150);
                        $this.removeClass('active');
                    }

                    var mytest = $this.next('.ajax-dropdown').find('.btn-group > .active > input').attr('id');
                    //console.log(mytest)

                    e.preventDefault();
                });

                if (scope.total > 0) {
                    var $badge = element.find('.badge');
                    $badge.addClass("bg-color-red bounceIn animated");
                }
            }
        };
    })

    .controller('ActivityContentController', ['$scope', function ($scope) {
        var ctrl = this;
        $scope.currentContent = '';
        ctrl.loadContent = function (content) {
            $scope.currentContent = content;
        }
    }])

    .directive('activityContent', ['$compile', function ($compile) {
        return {
            restrict: 'AE',
            transclude: true,
            require: '^activity',
            replace: true,
            scope: {
                footer: '=?'
            },
            controller: 'ActivityContentController',
            template: '\
        <div class="ajax-dropdown">\
          <div class="btn-group btn-group-justified" data-toggle="buttons" data-ng-transclude=""></div>\
          <div class="ajax-notifications custom-scroll">\
            <div class="alert alert-transparent">\
              <h4>Click a button to show messages here</h4>\
              This blank page message helps protect your privacy, or you can show the first message here automatically.\
            </div>\
            <i class="fa-solid fa-lock fa-4x fa-border"></i>\
          </div>\
          <span> {{ footer }}\
            <button type="button" data-loading-text="Loading..." data-ng-click="refresh($event)" class="btn btn-xs btn-default pull-right" data-activty-refresh-button="">\
            <i class="fa-solid fa-arrows-rotate"></i>\
            </button>\
          </span>\
        </div>',
            link: function (scope, element, attrs, activityCtrl) {
                scope.refresh = function (e) {
                    activityCtrl.refresh(e);
                };

                scope.$watch('currentContent', function (newContent, oldContent) {
                    if (newContent !== oldContent) {
                        var el = element.find('.ajax-notifications').html(newContent);
                        $compile(el)(scope);
                    }
                });
            }
        };
    }])

    .directive('activityItem', function () {
        return {
            restrict: 'AE',
            require: ['^activity', '^activityContent'],
            scope: {
                src: '=',
                onLoad: '=onload',
                active: '=?'
            },
            controller: function () {

            },
            transclude: true,
            replace: true,
            template: '\
        <label class="btn btn-default" data-ng-click="loadItem()" ng-class="{active: active}">\
          <input type="radio" name="activity">\
          <span data-ng-transclude=""></span>\
        </label>',
            link: function (scope, element, attrs, parentCtrls) {
                var activityCtrl = parentCtrls[0],
                    contentCtrl = parentCtrls[1];

                scope.$watch('active', function (active) {
                    if (active) {
                        activityCtrl.loadItem(scope, function (content) {
                            contentCtrl.loadContent(content);
                        });
                    }
                });
                activityCtrl.addItem(scope);

                scope.loadItem = function () {
                    scope.active = true;
                };
            }
        };
    });
