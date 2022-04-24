<!DOCTYPE html>
<html>

<?php
include 'scripts.php';
?>

<body>
    <form action="index.php" method="post">
        <input type="text" name="name" placeholder="Enter your ID number">
        <input type="submit" value="Submit">
    </form>

    <p>
        <?php
        if (isset($_POST['name'])) {
            echo tag('h1', "Hello " . $_POST['name']);

            $conn = database();
    
            $sql = "
                SELECT *
                FROM Orders NATURAL JOIN Cake
                WHERE custid = $_POST[name]
                ORDER BY ordertime DESC
            ";
            $result = $conn->query($sql);
    
            if ($result->num_rows > 0) {
            // output data of each row
            while($row = $result->fetch_assoc()) {
                echo '<div>';
                    echo tag('h1', $row["cakename"]);
                    $params = array(
                        'cakeid' => $row["cakeid"],
                        'custid' => $_POST['name']
                    );
                    $get_query = http_build_query(array_merge($_GET, $params), '', '&amp;');
                    echo tag('p', 'Order Time: ' . $row['ordertime']);
                    echo tag('p', 'Pickup Time:' . $row["pickuptime"]);
                    echo tag('p', 'Price:' . $row["pricepaid"]);
                    echo '<a href="/cake.php?' . $get_query . '">more info</a>';
                echo'</div>';

            }
            } else {
            echo "0 results";
            }
            $conn->close();
        }
        ?>
    </p>
</body>

</html
