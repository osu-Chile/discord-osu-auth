<?php 
session_start();
?>

<?php
if (isset($_GET['code'])) {
    // set post fields
    $post = [
        'client_id' => <CLIENTID>,
        'client_secret' => 'YOURTOKEN',
        'code'   => $_GET['code'],
        'grant_type' => 'authorization_code',
        'redirect_uri' => 'https://domain.com/auth'
    ];

    $ch = curl_init('https://osu.ppy.sh/oauth/token');
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $post);

    // execute!
    $response = json_decode(curl_exec($ch), true);

    // close the connection, release resources used
    curl_close($ch);

    $headers = [
        'Authorization: Bearer ' . $response['access_token'],
        'Content-Type: application/json'
    ];

    $curl = curl_init();
    curl_setopt($curl, CURLOPT_URL, "https://osu.ppy.sh/api/v2/me");
    curl_setopt($curl, CURLOPT_HTTPHEADER, $headers);
    curl_setopt($curl, CURLOPT_RETURNTRANSFER, TRUE);
    $userData = json_decode(curl_exec($curl), true);
    curl_close($curl);

    $_SESSION['id'] = $userData['id'];
}
?>

<head>
    <meta charset="utf-8">
    <title>osu!Chile Auth</title>
    <link rel="stylesheet" type="text/css" href="main.css">
</head>


<body>
    <img src="LOGOLINK" />
    <div class="cont">
        <h1>Tu solicitud está siendo procesada.</h1>
        <h3>Deberías recibir mayor información en unos instantes vía Discord.</h3>

    </div>
</body>


<?php
// create curl resource
$url = "http://127.0.0.1:5050/?osuid=" . $_SESSION['id'] . "&disid=" . $_SESSION['discord'];

$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
$output = curl_exec($ch);
curl_close($ch);    

?>

<?php
session_end();
?>