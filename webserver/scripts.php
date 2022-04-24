<?php
function tag($tag, $content) {
    return "<$tag>$content</$tag>";
}

function database() {
    $servername = "db";
    $username = "root";
    $password = "example";
    $dbname = "bakery";
    // Create connection
    $conn = new mysqli($servername, $username, $password, $dbname);
    // Check connection
    if ($conn->connect_error) {
        die("Connection failed: " . $conn->connect_error);
    }
    return $conn;
}
?>
