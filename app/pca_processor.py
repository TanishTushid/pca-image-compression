
from io import BytesIO
import numpy as np
from PIL import Image
from sklearn.decomposition import PCA


# Higher resolution is always tried before lower resolution.
SCALES = [1.0, 0.85, 0.70, 0.55, 0.40, 0.25, 0.15, 0.10]
JPEG_QUALITIES = [95, 85, 75, 65, 50, 35, 20, 10]
MAX_PIXELS = 1_000_000


def encode_jpeg(array, quality):
    buffer = BytesIO()
    Image.fromarray(array).save(
        buffer,
        format="JPEG",
        quality=quality,
        optimize=True,
    )
    return buffer.getvalue()


def compress_image(image_bytes: bytes, target_mb: float):
    if not 0 < target_mb <= 10:
        raise ValueError("Target must be greater than 0 and at most 10 MB.")

    target_bytes = int(target_mb * 1024 * 1024)

    with Image.open(BytesIO(image_bytes)) as source:
        source.load()
        original = source.convert("RGB")

    original_width, original_height = original.size

    # Limit computation for large uploads.
    if original_width * original_height > MAX_PIXELS:
        factor = (MAX_PIXELS / (original_width * original_height)) ** 0.5
        new_size = (
            max(1, int(original_width * factor)),
            max(1, int(original_height * factor)),
        )
        original = original.resize(new_size, Image.Resampling.LANCZOS)

    for scale in SCALES:
        width = max(1, int(original.width * scale))
        height = max(1, int(original.height * scale))

        if (width, height) == original.size:
            current = original
        else:
            current = original.resize(
                (width, height), Image.Resampling.LANCZOS
            )

        X = np.asarray(current, dtype=np.float64)
        max_components = min(X.shape[:2])

        # Try the highest component count first.
        candidates = sorted(
            {
                max_components,
                min(100, max_components),
                min(50, max_components),
                min(25, max_components),
                min(10, max_components),
                min(5, max_components),
                1,
            },
            reverse=True,
        )

        for k in candidates:
            reconstructed_channels = []
            explained_variances = []
            for channel in range(3):
                channel_data = X[:, :, channel]
                if np.var(channel_data, axis=0).sum() == 0:
                    reconstructed_channels.append(channel_data)
                    explained_variances.append(1.0)
                    continue

                pca = PCA(n_components=k, svd_solver="full")
                scores = pca.fit_transform(channel_data)
                reconstructed_channels.append(pca.inverse_transform(scores))
                explained_variances.append(
                    float(pca.explained_variance_ratio_.sum())
                )

            reconstructed = np.stack(reconstructed_channels, axis=2)
            pixels = np.clip(reconstructed, 0, 255).astype(np.uint8)

            # Try higher JPEG quality before lower quality.
            for quality in JPEG_QUALITIES:
                encoded = encode_jpeg(pixels, quality)

                if len(encoded) <= target_bytes:
                    mse = float(np.mean((X - pixels.astype(float)) ** 2))
                    psnr = (
                        float("inf")
                        if mse == 0
                        else float(10 * np.log10(255**2 / mse))
                    )

                    return {
                        "image_bytes": encoded,
                        "width": width,
                        "height": height,
                        "components": k,
                        "jpeg_quality": quality,
                        "original_size_bytes": len(image_bytes),
                        "output_size_bytes": len(encoded),
                        "target_size_bytes": target_bytes,
                        "target_met": True,
                        "mse": float(mse),
                        "psnr": psnr,
                        "explained_variance": float(
                            np.mean(explained_variances) * 100
                        ),
                    }

    # No tested combination met the requested target.
    raise ValueError(
        "Target size could not be reached within the supported "
        "resolution and quality limits. Try a larger target size."
    )
