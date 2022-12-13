/*********************************************************************************************************************
*  Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.                                           *
*                                                                                                                    *
*  Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance    *
*  with the License. A copy of the License is located at                                                             *
*                                                                                                                    *
*      http://www.apache.org/licenses/LICENSE-2.0                                                                    *
*                                                                                                                    *
*  or in the 'license' file accompanying this file. This file is distributed on an 'AS IS' BASIS, WITHOUT WARRANTIES *
*  OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific language governing permissions    *
*  and limitations under the License.                                                                                *
*********************************************************************************************************************/

/**
 * @author Solution Builders
 */

'use strict';

angular.module('dataLake.forgot', [])

.config(['$stateProvider', '$urlRouterProvider', function($stateProvider, $urlRouterProvider) {
    $stateProvider.state('forgot', {
        url: '/forgot',
        views: {
            '': {
                templateUrl: 'forgot/forgot.html',
                controller: 'ForgotCtrl'
            }
        },
        activeWithFederation: false
    });
}])

.controller('ForgotCtrl', function($scope, $state, authService) {

    $scope.message = '';
    $scope.errormessage = '';
    $scope.showVerification = false;
    $scope.user = {};

    $scope.forgotPassword = function(user, isValid) {
        $scope.message = '';
        $scope.errormessage = '';
        if (isValid) {
            authService.forgot(user).then(function(code) {
                if (code === 'INVITE_RESENT') {
                    $scope.message = 'Invite resent. Please check your email inbox.';
                } else {
                    $scope.showVerification = true;
                    $scope.user.email = user.email;
                }
            }, function(msg) {
                $scope.errormessage = 'An unexpected error has occurred. Please try again.';
                return;
            });

        } else {
            $scope.errormessage = 'There are still invalid fields.';
        }
    };

    $scope.changePassword = function(user, isValid) {
        $scope.message = '';
        $scope.errormessage = '';
        if (isValid) {
            authService.resetPassword(user).then(function() {
                $state.go('signin', {});
            }, function(msg) {
                $scope.errormessage = 'An unexpected error has occurred. Please try again.';
                return;
            });

        } else {
            $scope.errormessage = 'There are still invalid fields.';
        }
    };

});
