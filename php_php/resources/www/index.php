<?php
// Served by `php -S` in the php/php test. Both markers below exist only in PHP's output, not in
// this source, so a page that shows them was run by the PHP interpreter rather than served raw.
$sum = 20 + 22;
?>
<!DOCTYPE html>
<html>
<head>
<title><?php echo "PHP Server Test " . $sum; ?></title>
</head>
<body style="font-family: Segoe UI, sans-serif; font-size: 48px;">
<h1><?php echo "PHP Server Test " . $sum; ?></h1>
<p>PHP <?php echo PHP_VERSION; ?> (<?php echo PHP_SAPI; ?>)</p>
</body>
</html>
