# LMS
Library Management System

# Routes:

    - /login
        get: render_template
        post: redirect
    - /signup
        get: render_template
        post: redirect
    - /books
        - /
            get: render_template
        - /add
            get: render_template
            post: self, redirect
        - /viewAll
            get: render_template
            post: redirect
        - /delete
            get: render_template
            post: self, redirect
    - /author
        - /
            get: render_template
            post: redirect
        - /add
            get: render_template
            post: redirect
        - /viewAll
            get: render_template
            post: redirect
        - /delete
            get: render_template
            post: redirect