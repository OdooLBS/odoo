# -*- coding: utf-8 -*-
{
    'name': "JWT Authentication API for Odoo",

    'summary': """
        A module for implementing JWT-based authentication for mobile apps and external systems in Odoo.
        This module provides secure authentication using JSON Web Tokens (JWT) and supports token refresh.""",

    'description': """
        JWT Authentication API for Odoo provides a mechanism for secure login and API access using JSON Web Tokens (JWT). 
        This module allows mobile applications, third-party systems, or any external clients to authenticate users through 
        a token-based system. It provides endpoints for logging in, refreshing tokens, and securing API resources with JWT 
        authentication. 

        Key Features:
        - User login with JWT token issuance.
        - Token refresh endpoint to extend the session.
        - Decorators for protecting API routes, ensuring only authenticated users can access.
        - Integration with Odoo's internal authentication system.
        - Easy to extend and integrate with existing Odoo modules.

        This is ideal for mobile applications and other systems that require secure, stateless communication with Odoo.
    """,

    'author': "Mahmoud Abdel Latif",
    'website': "https://www.mah007.net",

    'category': 'Authentication/Tools',
    'version': '1.0',

    # Dependencies for this module to work correctly
    'depends': ['base', 'web'],

    # Always loaded
    'data': [
        # XML, CSV, or any other configuration files for the module can be loaded here.
        # Example: 'security/ir.model.access.csv',
    ],

    # Demo data (only loaded in demonstration mode)
    'demo': [
        # Example: 'demo/demo.xml',
    ],

    'license': 'LGPL-3',

    # Specify whether this module is installable and categorized as an application
    'installable': True,
    'application': True,

    # Define module loading sequence priority
    'sequence': 10,
}
