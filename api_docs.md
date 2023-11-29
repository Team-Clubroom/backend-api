## Login and Registration

/register ['POST']
----------------------------------------------------

```
Request: 
{ 
    user_first_name: string,
    user_last_name: string,
    email: string,
    password: string 
}
```

```
Response: { message: string }
```

Request's `email` is checked against records in `db.users`. If no matching `email` is found, new record in `db.users` is
created with `access_permissions` = `Null` and `pending_registr_expiry_datetime` equal to the current date-time plus 72
hours. Also, an email is sent with a JWT which expires as of the `pending_registr_expiry_datetime`. If matching `email`
is found in `db.users` with `access_permissions` = `Null`, then an email is sent with an updated JWT, and
the `pending_registr_expiry_datetime` is updated in `db.users`. If matching `email` is found in `db.users`
with `access_permissions` not `Null`, then an error is returned indicating that the request's `email` is already
associated with a validated account.

/login ['POST']
----------------------------------------------------

```
Request: { email: string, password: string }
```

```
Response: 
{ 
    message: string,
    data: {
        jwt: string,
        isAdmin: boolean,
        email: string,
        firstName: string,
        lastName: string
    } 
}
```

Generates a JWT using the server's secret key if the `email` and `password` match a record in the `users` table

/verify ['GET']
----------------------------------------------------

```
Request: URL_PARAM({ jwt: string })
```

```
Response: <HTML/>
```

Given a valid JWT token as a URL query parameter, the `access_permissions` field is updated in the `users` table

## Data routes

/employer ['POST'] @admin
----------------------------------------------------

```
Request:
{   
    employer_name: string,
    employer_addr_line_1: string,
    employer_addr_line_2: string | null,
    employer_addr_city: string,
    employer_addr_state: string,
    employer_addr_zip_code: string,
    employer_founded_date: "MM-DD-YYYY",
    employer_dissolved_date: "MM-DD-YYYY" | null,
    employer_bankruptcy_date: "MM-DD-YYYY" | null,
    employer_industry_sector_code: number,
    employer_status: string,
    employer_legal_status: string,
    
}
```

```
Response:
{
    data: {
        employer_id: number,
    }
    message: "New employer added",
}
```

/employers ['GET'] @private
----------------------------------------------------

```
Request: {}
```

```
Response: 
{
   data: [
      {
          id: string,
          name: string,
          address: {
              line1: string,
              line2: string,
              city: string,
              state: string,
              zipCode: string,
          },
          foundedDate: string,
          dissolvedDate: string,
          bankruptcyDate: string,
          industrySectorCode: number,
          status: string,
          legalStatus: string,
      },
      (...)
   ],
   message: "n employers fetched"
}
```

Returns a list of employers

/employers-graph ['GET'] @private
----------------------------------------------------

```
Request: { employer_name: string }
```

```
Response:
{
    data: {
        nodes: {
            "<employer_id>": {
                name: string,
                estDate: string,
                position: { x: number, y: number }
            },
            (...)
        },
        edges: [
            {
                id: string,
                source: string,
                target: string,
                relationType: "Merger" | "Split" | "Subsidiary"
            },
            (...)
        ],
    },
    message: "Employer graph fetched successfully"
}
```

Returns a tree which includes the searched employer.

## Email service

google_script_url
----------------------------------------------------

```
Request: {first_name: string; email: string; verification_url: string; admin_token: string}
```

```
Response: {}
```

Sends an HTML template email with a verification url. Consult admin for actual `google_script_url` value as well
as `admin_token` value
