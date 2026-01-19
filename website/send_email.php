<?php
use PHPMailer\PHPMailer\PHPMailer;
use PHPMailer\PHPMailer\Exception;

// Include PHPMailer (you need to download and place in the same directory)
// Download from: https://github.com/PHPMailer/PHPMailer
require 'PHPMailer/src/Exception.php';
require 'PHPMailer/src/PHPMailer.php';
require 'PHPMailer/src/SMTP.php';

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['error' => 'Method not allowed']);
    exit;
}

try {
    $mail = new PHPMailer(true);

    // SMTP configuration
    $mail->isSMTP();
    $mail->Host = 'mail.mydgv.com';
    $mail->SMTPAuth = true;
    $mail->Username = 'dgv@mydgv.com';
    $mail->Password = '0123456789';
    $mail->SMTPSecure = PHPMailer::ENCRYPTION_STARTTLS;
    $mail->Port = 587;

    // Recipients
    $mail->setFrom('dgv@mydgv.com', 'Maharaja Chef Services');
    $mail->addAddress('contact@myDGV.com');

    // Get form data
    $formData = $_POST;

    // Determine email content based on form type
    if (isset($formData['event-type'])) {
        // Booking form
        $mail->Subject = 'New Chef Booking Request from ' . ($formData['name'] ?? 'Unknown');

        $body = "New Booking Request:\n\n";
        $body .= "Name: " . ($formData['name'] ?? '') . "\n";
        $body .= "Email: " . ($formData['email'] ?? '') . "\n";
        $body .= "Phone: " . ($formData['phone'] ?? '') . "\n";
        $body .= "Event Type: " . ($formData['event-type'] ?? '') . "\n";
        $body .= "Date & Time: " . ($formData['date-time'] ?? '') . "\n";
        $body .= "Location: " . ($formData['location'] ?? '') . "\n";
        $body .= "Number of Guests: " . ($formData['guests'] ?? '') . "\n";
        $body .= "Dietary Preferences: " . ($formData['dietary'] ?? '') . "\n";
        $body .= "Message: " . ($formData['message'] ?? '') . "\n";
    } else {
        // Contact form
        $mail->Subject = 'New Contact Message from ' . ($formData['name'] ?? 'Unknown');

        $body = "New Contact Message:\n\n";
        $body .= "Name: " . ($formData['name'] ?? '') . "\n";
        $body .= "Email: " . ($formData['email'] ?? '') . "\n";
        $body .= "Message:\n" . ($formData['message'] ?? '') . "\n";
    }

    $mail->Body = $body;

    $mail->send();

    echo json_encode(['success' => true, 'message' => 'Email sent successfully']);

} catch (Exception $e) {
    http_response_code(500);
    echo json_encode(['error' => 'Failed to send email: ' . $mail->ErrorInfo]);
}
?>
