/*

This program has been developed by students from the bachelor Computer Science at
Utrecht University within the Software Project course.
© Copyright Utrecht University (Department of Information and Computing Sciences)

 */

import * as React from 'react'
import { Navbar } from "react-bootstrap";
import { useKeycloak } from "@react-keycloak/web";

/**If a user is logged in, this will display the text "Signed in as: {username}" */
export const LoggedInUser = () => {

    //Obtain keycloak
    const { keycloak } = useKeycloak()
    console.log(keycloak)
    return (
        <Navbar.Text>
            {
                keycloak.authenticated && keycloak.tokenParsed && <>Logged in as: {keycloak.tokenParsed['name']}</>
            }
        </Navbar.Text>
    )
}