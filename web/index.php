<?php 
session_start();
?>
<!doctype html>
<html lang="en">

<head>
    <meta charset="utf-8">
    <title>osu!Chile Auth</title>
    <link rel="stylesheet" type="text/css" href="main.css">
</head>

<body>
    <img src="LOGOLINK"/>
    <div class="cont">
        <?php 
if(isset($_GET['discord'])) {
$_SESSION['discord'] = $_GET['discord'];
?>
<?php 

$discord = $_SESSION['discord'];
if (is_numeric($discord)){
    
?>

        <h1>Ingresa con tu cuenta de osu!</h1>
        <form action="https://osu.ppy.sh/oauth/authorize" method="GET" class="opl-login">
            <input type="hidden" name="response_type" value="code">
            <input type="hidden" name="client_id" value="PUTYOURIDHERE">
            <input type="hidden" name="redirect_uri" value='https://domain.com/auth'>
            <input type="submit" class="your button css classes" value="Ingresar">
        </form>
        <h3>¿Por qué necesito esto?</h3>
        <p>Ingresando con tu cuenta de osu!, podemos identificar quien eres dentro del juego más fácil.<br>Esto también nos sirve para verificar tu identidad. | Por favor, ingresa antes a tu cuenta en <a style="color: white !important" href="https://osu.ppy.sh/">https://osu.ppy.sh/<a></p>
            <p style="opacity: 0.5"><br>Información<br>Discord: <?php echo $_GET['discord']?></p>

            <?php
}}

?>


    <?php 
if(isset($_GET['discord'])) {
$_SESSION['discord'] = $_GET['discord'];
?>
<?php
if (!is_numeric($discord)){ ?>


        <h1>DiscordID incorrecta.</h1>
        <h3>Si crees que esto es un error, puedes contactar a un administrador en nuestro Discord.</h3>
        <p style="opacity: 0.5"><br>Codigo de error: 0x0002</p>
    <?php } ?>

<?php }else{ ?>
            <h1>URL incorrecta.</h1>
        <h3>Si crees que esto es un error, puedes contactar a un administrador en nuestro Discord.</h3>
        <p style="opacity: 0.5"><br>Codigo de error: 0x0001</p>

        
<?php } ?>





    </div>
</body>

</html>