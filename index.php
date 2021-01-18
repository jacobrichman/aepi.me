<?php
$spreadsheet_url=$_ENV["SPREADSHEET_URL"];
echo "url: ".$spreadsheet_url;

if(!ini_set('default_socket_timeout', 15)) echo "<!-- unable to change socket timeout -->";

$get = strtolower(preg_replace('/\s+/', '', $_GET['path']));

if (($handle = fopen($spreadsheet_url, "r")) !== FALSE) {
  while (($data = fgetcsv($handle, 1000, ",")) !== FALSE) {
    $extension = strtolower(preg_replace('/\s+/', '', $data[1]));
    
    if($extension==$get){
      $redirect = $data[2];
    }
  }
  fclose($handle);
}
else{
  die("Error reading Google Sheet.");
}
?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">

<!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=UA-58617131-14"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'UA-58617131-14');
</script>


  <?php
  if($redirect){
    echo '<script>window.location = "'.$redirect.'";</script>';
  }elseif(!$_GET['path']){
    echo 'Welcome to aepi.me!';
  }else{
    echo "URL could not be found :(";
  }
  ?>

</html>
