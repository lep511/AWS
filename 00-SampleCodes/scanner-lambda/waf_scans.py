def predefined_tests():
    response = [
        {
            "Id": "11",
            "Name": "CanaryGET",
            "Type": "Canary",
            "Method": "GET",
            "Group": "WSW",
            "exec_string": {
                "url": {},
                "uri": "/index.php",
                "headers": {
                    "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
                    "X-SyntheticKey": "ShiftLeft123"
                },
                "data": {},
                "json": {},
                "method": "get",
                "timeout": 5
            }
        },
        {
            "Id": "12",
            "Name": "CanaryPOST",
            "Type": "Canary",
            "Method": "POST",
            "Group": "WSW",
            "exec_string": {
                "url": {},
                "uri": "/index.php",
                "data": {},
                "json": {},
                "headers": {
                    "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
                    "X-SyntheticKey": "ShiftLeft123"
                },
                "method": "post",
                "timeout": 5
            }
        },
        {
            "Id": "13",
            "Name": "CanaryAPI",
            "Type": "Canary",
            "Method": "POST",
            "Group": "WSW",
            "exec_string": {
                "url": {},
                "uri": "/api/listproducts.php",
                "data": {},
                "json": {
                    "numrecords": "3"
                },
                "headers": {
                    "Content-Type": "application/json; charset=utf-8"
                },
                "method": "post",
                "timeout": 5
            }
        },
        {
            "Id": "14",
            "Name": "CanaryBotStatic",
            "Type": "Canary",
            "Method": "GET",
            "Group": "WSW",
            "exec_string": {
                "url": {},
                "uri": "/files/ui.css",
                "headers": {
                    "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
                    "User-Agent": "ZyBorg/1.0"
                },
                "data": {},
                "json": {},
                "method": "get",
                "timeout": 5
            }
        },
        {
            "Id": "15",
            "Name": "SQLiQueryString",
            "Type": "SQLi",
            "Method": "GET",
            "Group": "WSW",
            "exec_string": {
                "url": {},
                "uri": "/product.php?id=-260479%2F**%2F%2F*!union*%2F%2F**%2F%2F*!select*%2F%2F**%2Fconcat(username%2C0x3a%2Cpassword%2C0x3a%2Cusertype)%2F**%2F%2F*!from*%2F%2F**%2Fjos_users%2F**%2F\"",
                "data": {},
                "json": {},
                "headers": {
                    "Content-Type": "application/x-www-form-urlencoded; charset=utf-8"
                },
                "method": "get",
                "timeout": 5
            }
        },
        {
            "Id": "16",
            "Name": "SQLiCookie",
            "Type": "SQLi",
            "Method": "GET",
            "Group": "WSW",
            "exec_string": {
                "url": {},
                "uri": "/product.php?id=32574938",
                "headers": {
                    "Cookie": "PHPSESSID=-260479%2F**%2F%2F*!union*%2F%2F**%2F%2F*!select*%2F%2F**%2Fconcat(username%2C0x3a%2Cpassword%2C0x3a%2Cusertype)%2F**%2F%2F*!from*%2F%2F**%2Fjos_users%2F**%2F",
                    "Content-Type": "application/x-www-form-urlencoded; charset=utf-8"
                },
                "data": {},
                "json": {},
                "method": "get",
                "timeout": 5
            }
        },
        {
            "Id": "17",
            "Name": "XSSQueryString",
            "Type": "WSW",
            "Method": "GET",
            "Group": "WSW",
            "exec_string": {
                "url": {},
                "uri": "/product.php?id=<script%20src%3D\"http%3A%2F%2F127.0.0.1%2Fxss_malware.js\">\"",
                "headers": {
                    "Content-Type": "application/x-www-form-urlencoded; charset=utf-8"
                },
                "method": "get",
                "data": {},
                "json": {},
                "timeout": 5
            }
        },
        {
            "Id": "18",
            "Name": "XSSBody",
            "Type": "XSS",
            "Method": "POST",
            "Group": "WSW",
            "exec_string": {
                "url": {},
                "uri": "/",
                "data": {
                    "/product.phpreviewEmail": "Hacker@Hacker.com",
                    "reviewName": "Hacker",
                    "reviewStory": "<script>alert(\"Hello World!\")<script/>",
                    "reviewSubmit": "Submit",
                    "reviewTitle": "Hacked"
                },
                "json": {},
                "headers": {
                    "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
                    "User-Agent": "HTTPie/1.0.3-dev"
                },
                "method": "post",
                "timeout": 5
            }
        },
        {
            "Id": "19",
            "Name": "PathTraversal",
            "Type": "Traversal",
            "Method": "GET",
            "Group": "WSW",
            "exec_string": {
                "url": {},
                "uri": "/download.php?form=..%2Fmodules%2Freviews.php",
                "headers": {
                    "Content-Type": "application/x-www-form-urlencoded; charset=utf-8"
                },
                "data": {},
                "json": {},
                "method": "get",
                "timeout": 5
            }
        },
        {
            "Id": "20",
            "Name": "IncludesModules",
            "Type": "Includes",
            "Method": "GET",
            "Group": "WSW",
            "exec_string": {
                "url": {},
                "uri": "/includes/index.html",
                "headers": {
                    "Content-Type": "application/x-www-form-urlencoded; charset=utf-8"
                },
                "data": {},
                "json": {},
                "method": "get",
                "timeout": 5
            }
        },
        {
            "Id": "21",
            "Name": "BadBot",
            "Type": "BadBot",
            "Method": "GET",
            "Group": "WSW",
            "exec_string": {
                "url": {},
                "uri": "/index.php",
                "headers": {
                    "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
                    "User-Agent": "ZyBorg/1.0"
                },
                "data": {},
                "json": {},
                "method": "get",
                "timeout": 5
            }
        },
        {
            "Id": "22",
            "Name": "APIMisuse",
            "Type": "APIMisuse",
            "Method": "POST",
            "Group": "WSW",
            "exec_string": {
                "url": {},
                "uri": "/api/listproducts.php",
                "data": {},
                "json": {
                    "numrecords": "200"
                },
                "headers": {
                    "Content-Type": "application/json; charset=utf-8"
                },
                "method": "post",
                "timeout": 5
            }
        },
        {
            "Id": "23",
            "Name": "MysteryTest",
            "Type": "CTF",
            "Method": "GET",
            "Group": "WSW",
            "exec_string": {
                "url": {},
                "uri": "/",
                "headers": {
                    "MysteryHint": "U2VjdXJpdHkgaXMgam9iIHplcm8h"
                },
                "method": "get",
                "data": {},
                "json": {},
                "timeout": 5
            }
        }
    ]
    return (response)