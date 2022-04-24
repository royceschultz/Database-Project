<!DOCTYPE html>
<html>

<?php
include 'scripts.php';
?>

<body>
    <!-- php script -->
    <?php
        
        // if cakeid is defined
        if (isset($_GET['cakeid'])) {
            // connect to db
            $conn = database();

            // Lookup cake name
            $sql = "
                SELECT *
                FROM Cake
                WHERE cakeid = $_GET[cakeid]
            ";
            $result = $conn->query($sql);
            $cakename = '';
            if ($result->num_rows > 0) {
                // output data of each row
                while($row = $result->fetch_assoc()) {
                    $cakename = $row["cakename"];
                }
            }
            echo tag('h1', "Ingredients for " . $cakename);

            // sql query
            $sql = "
                SELECT Ingredient.*, Contain.*
                FROM Cake NATURAL JOIN Contain JOIN Ingredient on Contain.ingredid = Ingredient.ingredid
                WHERE cakeid = 1
            ";
            // execute query
            $result = $conn->query($sql);
            // if there are results
            if ($result->num_rows > 0) {
                // output data of each row
                while($row = $result->fetch_assoc()) {
                    // echo implode(',', array_keys($row)) . "<br>";
                    // echo implode(',', $row) . "<br>";
                    echo tag('p', $row["qty"] . ' ' . $row["iname"]);
                }
            } else {
                echo "0 results";
            }

        }
    ?>
</body>

</html
