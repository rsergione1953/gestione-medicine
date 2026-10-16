package it.spsoft.gestionemedicine;

import android.app.Activity;
import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.media.AudioAttributes;
import android.media.RingtoneManager;
import android.print.PrintAttributes;
import android.print.PrintManager;
import android.webkit.JavascriptInterface;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebView;
import android.webkit.WebViewClient;

import java.nio.charset.StandardCharsets;
import java.util.Map;

public class MedicineActivity extends Activity {
    private static final int FILE_CHOOSER_REQUEST = 42;
    private static final int NOTIFICATION_PERMISSION_REQUEST = 43;
    private static final String NOTIFICATION_CHANNEL_ID = "medicine_low_stock";
    private WebView webView;
    private ValueCallback<Uri[]> fileChooserCallback;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        createNotificationChannel();
        webView = new WebView(this);
        webView.getSettings().setJavaScriptEnabled(true);
        webView.getSettings().setDomStorageEnabled(true);
        webView.setWebViewClient(new WebViewClient());
        webView.setWebChromeClient(new WebChromeClient() {
            @Override
            public boolean onShowFileChooser(
                    WebView view,
                    ValueCallback<Uri[]> callback,
                    FileChooserParams params) {
                if (fileChooserCallback != null) fileChooserCallback.onReceiveValue(null);
                fileChooserCallback = callback;
                try {
                    startActivityForResult(params.createIntent(), FILE_CHOOSER_REQUEST);
                    return true;
                } catch (RuntimeException error) {
                    fileChooserCallback = null;
                    callback.onReceiveValue(null);
                    return false;
                }
            }
        });
        webView.addJavascriptInterface(new Object() {
            @JavascriptInterface
            public void printPage() {
                runOnUiThread(() -> {
                    PrintManager printManager = (PrintManager) getSystemService(PRINT_SERVICE);
                    if (printManager != null) {
                        printManager.print(
                                "Gestione Medicine",
                                webView.createPrintDocumentAdapter("Gestione Medicine"),
                                new PrintAttributes.Builder()
                                        .setMediaSize(PrintAttributes.MediaSize.ISO_A4)
                                        .build());
                    }
                });
            }

            @JavascriptInterface
            public boolean hasNotificationPermission() {
                return canPostNotifications();
            }

            @JavascriptInterface
            public void requestNotificationPermission() {
                runOnUiThread(() -> {
                    if (Build.VERSION.SDK_INT >= 33
                            && checkSelfPermission(android.Manifest.permission.POST_NOTIFICATIONS)
                                    != PackageManager.PERMISSION_GRANTED) {
                        requestPermissions(
                                new String[] {android.Manifest.permission.POST_NOTIFICATIONS},
                                NOTIFICATION_PERMISSION_REQUEST);
                    } else {
                        notifyWebViewOfPermission(canPostNotifications());
                    }
                });
            }

            @JavascriptInterface
            public void showLowStock(
                    String medicineId, String medicineName, int quantity, boolean playAlert) {
                if (medicineId == null || medicineId.isEmpty()
                        || medicineName == null || medicineName.trim().isEmpty()
                        || quantity < 0) {
                    return;
                }
                runOnUiThread(() ->
                        showLowStockNotification(medicineId, medicineName, quantity, playAlert));
            }

            @JavascriptInterface
            public void clearLowStock(String medicineId) {
                if (medicineId == null || medicineId.isEmpty()) return;
                runOnUiThread(() -> {
                    NotificationManager manager =
                            (NotificationManager) getSystemService(NOTIFICATION_SERVICE);
                    if (manager != null) manager.cancel(notificationIdFor(medicineId));
                });
            }
        }, "NativeApp");
        setContentView(webView);
        webView.loadUrl("file:///android_asset/index.html");
    }

    private void createNotificationChannel() {
        if (Build.VERSION.SDK_INT < 26) return;
        NotificationChannel channel = new NotificationChannel(
                NOTIFICATION_CHANNEL_ID,
                "Avvisi scorta medicine",
                NotificationManager.IMPORTANCE_HIGH);
        channel.setDescription("Avvisa quando un farmaco raggiunge la soglia minima.");
        channel.enableVibration(true);
        channel.setSound(
                RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION),
                new AudioAttributes.Builder()
                        .setUsage(AudioAttributes.USAGE_NOTIFICATION)
                        .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION)
                        .build());
        NotificationManager manager = getSystemService(NotificationManager.class);
        if (manager != null) manager.createNotificationChannel(channel);
    }

    private boolean canPostNotifications() {
        if (Build.VERSION.SDK_INT >= 33
                && checkSelfPermission(android.Manifest.permission.POST_NOTIFICATIONS)
                        != PackageManager.PERMISSION_GRANTED) {
            return false;
        }
        NotificationManager manager =
                (NotificationManager) getSystemService(NOTIFICATION_SERVICE);
        return manager != null
                && (Build.VERSION.SDK_INT < 24 || manager.areNotificationsEnabled());
    }

    private void notifyWebViewOfPermission(boolean granted) {
        if (webView != null) {
            webView.evaluateJavascript(
                    "window.onNativeNotificationPermission("
                            + (granted ? "true" : "false") + ")",
                    null);
        }
    }

    private void showLowStockNotification(
            String medicineId, String medicineName, int quantity, boolean playAlert) {
        if (!canPostNotifications()) return;

        int notificationId = notificationIdFor(medicineId);
        Intent openApp = new Intent(this, MedicineActivity.class);
        openApp.setFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_SINGLE_TOP);
        PendingIntent contentIntent = PendingIntent.getActivity(
                this,
                notificationId,
                openApp,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);

        Intent acknowledge = new Intent(this, MedicineAcknowledgeReceiver.class);
        acknowledge.setAction(MedicineAcknowledgeReceiver.ACTION_ACKNOWLEDGE);
        acknowledge.setData(Uri.parse("medicine-alert://ack/" + Uri.encode(medicineId)));
        acknowledge.putExtra(
                MedicineAcknowledgeReceiver.EXTRA_NOTIFICATION_ID, notificationId);
        PendingIntent acknowledgeIntent = PendingIntent.getBroadcast(
                this,
                notificationId,
                acknowledge,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);

        String message = medicineName + " — " + quantity + " unità rimanenti";
        Notification.Builder builder = Build.VERSION.SDK_INT >= 26
                ? new Notification.Builder(this, NOTIFICATION_CHANNEL_ID)
                : new Notification.Builder(this)
                        .setPriority(Notification.PRIORITY_HIGH)
                        .setDefaults(playAlert ? Notification.DEFAULT_ALL : 0);
        builder.setSmallIcon(android.R.drawable.ic_dialog_alert)
                .setContentTitle("Scorta medicine in esaurimento")
                .setContentText(message)
                .setStyle(new Notification.BigTextStyle().bigText(message))
                .setCategory(Notification.CATEGORY_REMINDER)
                .setVisibility(Notification.VISIBILITY_PRIVATE)
                .setContentIntent(contentIntent)
                .setOngoing(true)
                .setAutoCancel(false)
                .setOnlyAlertOnce(!playAlert)
                .addAction(
                        android.R.drawable.ic_menu_info_details,
                        "Ho capito",
                        acknowledgeIntent);

        NotificationManager manager =
                (NotificationManager) getSystemService(NOTIFICATION_SERVICE);
        if (manager != null) {
            Notification notification = builder.build();
            notification.flags |= Notification.FLAG_NO_CLEAR;
            manager.notify(notificationId, notification);
        }
    }

    private int notificationIdFor(String medicineId) {
        SharedPreferences preferences =
                getSharedPreferences("medicine_notifications", MODE_PRIVATE);
        String key = "medicine_" + android.util.Base64.encodeToString(
                medicineId.getBytes(StandardCharsets.UTF_8),
                android.util.Base64.URL_SAFE | android.util.Base64.NO_WRAP
                        | android.util.Base64.NO_PADDING);
        int existing = preferences.getInt(key, 0);
        if (existing != 0) return existing;

        int candidate = preferences.getInt("next_id", 1000);
        Map<String, ?> values = preferences.getAll();
        while (isNotificationIdInUse(values, candidate)) {
            candidate = candidate == Integer.MAX_VALUE ? 1000 : candidate + 1;
        }
        int next = candidate == Integer.MAX_VALUE ? 1000 : candidate + 1;
        preferences.edit().putInt(key, candidate).putInt("next_id", next).apply();
        return candidate;
    }

    private boolean isNotificationIdInUse(Map<String, ?> values, int candidate) {
        for (Map.Entry<String, ?> entry : values.entrySet()) {
            if (entry.getKey().startsWith("medicine_")
                    && entry.getValue() instanceof Integer
                    && ((Integer) entry.getValue()) == candidate) {
                return true;
            }
        }
        return false;
    }

    @Override
    public void onRequestPermissionsResult(
            int requestCode, String[] permissions, int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == NOTIFICATION_PERMISSION_REQUEST) {
            notifyWebViewOfPermission(canPostNotifications());
        }
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == FILE_CHOOSER_REQUEST && fileChooserCallback != null) {
            fileChooserCallback.onReceiveValue(
                    WebChromeClient.FileChooserParams.parseResult(resultCode, data));
            fileChooserCallback = null;
        }
    }

    @Override
    protected void onDestroy() {
        if (fileChooserCallback != null) fileChooserCallback.onReceiveValue(null);
        if (webView != null) webView.destroy();
        super.onDestroy();
    }
}
